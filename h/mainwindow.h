#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QProcess>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    //void on_tableWidget_;

    void showEvent(QShowEvent *event);

    void on_btInsert_clicked();

    void on_btRemove_clicked();

    void on_btSave_clicked();

private:
    Ui::MainWindow *ui;
};

#endif // MAINWINDOW_H
