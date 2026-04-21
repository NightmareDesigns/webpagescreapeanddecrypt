#include "mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QLabel>
#include <QMessageBox>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QFileDialog>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , scraperProcess(nullptr)
{
    setupUI();
    setWindowTitle("Web Scraper & Decryptor");
    resize(1000, 700);
}

MainWindow::~MainWindow()
{
    if (scraperProcess && scraperProcess->state() != QProcess::NotRunning) {
        scraperProcess->kill();
        scraperProcess->waitForFinished();
    }
}

void MainWindow::setupUI()
{
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    // Input Group
    QGroupBox *inputGroup = new QGroupBox("Scraper Configuration", this);
    QFormLayout *formLayout = new QFormLayout(inputGroup);

    urlInput = new QLineEdit(this);
    urlInput->setPlaceholderText("https://example.com");
    formLayout->addRow("Start URL:", urlInput);

    maxPagesInput = new QSpinBox(this);
    maxPagesInput->setRange(1, 1000);
    maxPagesInput->setValue(30);
    formLayout->addRow("Max Pages:", maxPagesInput);

    maxDepthInput = new QSpinBox(this);
    maxDepthInput->setRange(1, 10);
    maxDepthInput->setValue(2);
    formLayout->addRow("Max Depth:", maxDepthInput);

    workersInput = new QSpinBox(this);
    workersInput->setRange(1, 32);
    workersInput->setValue(8);
    formLayout->addRow("Workers:", workersInput);

    timeoutInput = new QSpinBox(this);
    timeoutInput->setRange(1, 120);
    timeoutInput->setValue(10);
    formLayout->addRow("Timeout (s):", timeoutInput);

    mainLayout->addWidget(inputGroup);

    // Control Buttons
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    startButton = new QPushButton("Start Scraping", this);
    startButton->setStyleSheet("QPushButton { padding: 10px; font-size: 14px; font-weight: bold; }");
    connect(startButton, &QPushButton::clicked, this, &MainWindow::startScraping);
    buttonLayout->addWidget(startButton);
    buttonLayout->addStretch();

    mainLayout->addLayout(buttonLayout);

    // Progress Bar
    progressBar = new QProgressBar(this);
    progressBar->setRange(0, 0);
    progressBar->setVisible(false);
    mainLayout->addWidget(progressBar);

    // Status Text
    statusText = new QTextEdit(this);
    statusText->setMaximumHeight(100);
    statusText->setReadOnly(true);
    statusText->setPlaceholderText("Status messages will appear here...");
    mainLayout->addWidget(new QLabel("Status:", this));
    mainLayout->addWidget(statusText);

    // Results Display
    resultsDisplay = new QTextEdit(this);
    resultsDisplay->setReadOnly(true);
    resultsDisplay->setPlaceholderText("Results will appear here after scraping...");
    mainLayout->addWidget(new QLabel("Results:", this));
    mainLayout->addWidget(resultsDisplay);

    setCentralWidget(centralWidget);
}

void MainWindow::startScraping()
{
    QString url = urlInput->text().trimmed();
    if (url.isEmpty()) {
        QMessageBox::warning(this, "Input Error", "Please enter a valid URL.");
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        QMessageBox::warning(this, "Input Error", "URL must start with http:// or https://");
        return;
    }

    // Disable start button and show progress
    startButton->setEnabled(false);
    progressBar->setVisible(true);
    resultsDisplay->clear();
    statusText->clear();
    updateStatusMessage("Starting scraper...");

    // Create process if not exists
    if (!scraperProcess) {
        scraperProcess = new QProcess(this);
        connect(scraperProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
                this, &MainWindow::onProcessFinished);
        connect(scraperProcess, &QProcess::errorOccurred, this, &MainWindow::onProcessError);
        connect(scraperProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::onProcessOutput);
        connect(scraperProcess, &QProcess::readyReadStandardError, this, &MainWindow::onProcessOutput);
    }

    // Build command
    QStringList arguments;
    arguments << "scraper.py"
              << url
              << "--max-pages" << QString::number(maxPagesInput->value())
              << "--max-depth" << QString::number(maxDepthInput->value())
              << "--workers" << QString::number(workersInput->value())
              << "--timeout" << QString::number(timeoutInput->value());

    updateStatusMessage("Running: python " + arguments.join(" "));

    scraperProcess->start("python", arguments);
}

void MainWindow::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    startButton->setEnabled(true);
    progressBar->setVisible(false);

    if (exitStatus == QProcess::NormalExit && exitCode == 0) {
        updateStatusMessage("Scraping completed successfully!");

        // Read and parse JSON output
        QByteArray output = scraperProcess->readAllStandardOutput();
        QJsonDocument doc = QJsonDocument::fromJson(output);

        if (!doc.isNull()) {
            resultsDisplay->setPlainText(doc.toJson(QJsonDocument::Indented));

            // Parse and display summary
            QJsonObject obj = doc.object();
            int visitedPages = obj["visited_pages"].toInt();
            QString startUrl = obj["start_url"].toString();

            QString summary = QString("Scraping Summary:\n")
                            + "Start URL: " + startUrl + "\n"
                            + "Pages Visited: " + QString::number(visitedPages) + "\n\n";

            QJsonArray pages = obj["pages"].toArray();
            for (const QJsonValue &pageVal : pages) {
                QJsonObject page = pageVal.toObject();
                QString pageUrl = page["url"].toString();
                QString title = page["title"].toString();
                QJsonArray messages = page["decrypted_messages"].toArray();

                summary += "\n─────────────────────────────────\n";
                summary += "URL: " + pageUrl + "\n";
                if (!title.isEmpty()) {
                    summary += "Title: " + title + "\n";
                }
                summary += "Decrypted Messages (" + QString::number(messages.size()) + "):\n";

                for (const QJsonValue &msg : messages) {
                    summary += "  • " + msg.toString() + "\n";
                }
            }

            statusText->setPlainText(summary);
        } else {
            resultsDisplay->setPlainText(QString::fromUtf8(output));
        }
    } else {
        updateStatusMessage("Scraping failed with exit code: " + QString::number(exitCode));
        QString errorOutput = QString::fromUtf8(scraperProcess->readAllStandardError());
        if (!errorOutput.isEmpty()) {
            resultsDisplay->setPlainText("Error:\n" + errorOutput);
        }
    }
}

void MainWindow::onProcessError(QProcess::ProcessError error)
{
    startButton->setEnabled(true);
    progressBar->setVisible(false);

    QString errorMsg;
    switch (error) {
        case QProcess::FailedToStart:
            errorMsg = "Failed to start Python. Make sure Python is installed and in PATH.";
            break;
        case QProcess::Crashed:
            errorMsg = "Process crashed.";
            break;
        case QProcess::Timedout:
            errorMsg = "Process timed out.";
            break;
        default:
            errorMsg = "Unknown error occurred.";
            break;
    }

    updateStatusMessage("Error: " + errorMsg);
    QMessageBox::critical(this, "Process Error", errorMsg);
}

void MainWindow::onProcessOutput()
{
    // This can be used to show real-time output if needed
    // For now, we'll wait for the process to complete
}

void MainWindow::updateStatusMessage(const QString &message)
{
    statusText->append(message);
}
