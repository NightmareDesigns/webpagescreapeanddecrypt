#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLineEdit>
#include <QSpinBox>
#include <QPushButton>
#include <QTextEdit>
#include <QProgressBar>
#include <QProcess>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void startScraping();
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onProcessError(QProcess::ProcessError error);
    void onProcessOutput();

private:
    void setupUI();
    void updateStatusMessage(const QString &message);

    // UI Components
    QLineEdit *urlInput;
    QSpinBox *maxPagesInput;
    QSpinBox *maxDepthInput;
    QSpinBox *workersInput;
    QSpinBox *timeoutInput;
    QPushButton *startButton;
    QTextEdit *resultsDisplay;
    QProgressBar *progressBar;
    QTextEdit *statusText;

    // Process
    QProcess *scraperProcess;
};

#endif // MAINWINDOW_H
