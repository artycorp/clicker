#include "h/mainwindow.h"
#include "ui_mainwindow.h"
#include "h/logdialog.h"
#include "ui_logdialog.h"
#include <qdebug.h>
#include <qfile.h>
#include <qjson/parser.h>
#include <qjson/serializer.h>
#include <QTableWidget>
#include<QMessageBox>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}
QTableWidgetItem* initValue(QString str)
{
    QTableWidgetItem* item = new QTableWidgetItem(str);
    item->setTextAlignment(Qt::AlignCenter | Qt::AlignVCenter);
    return item;
}

void ReadJson(QTableWidget* table)
{
    //QString val;
    bool ok;
    QFile file;
    file.setFileName("settings.json");
    file.open(QIODevice::ReadOnly | QIODevice::Text);
    QJson::Parser parser;
    QVariantMap res = parser.parse(&file,&ok).toMap();
    //val = file.readAll();
    file.close();
    //qDebug() << res;

    if (ok){        
        table->setRowCount(0);
        int i = 0;
        foreach(QVariant search_text, res["search_texts"].toList()){
            int j = 0;
            QVariantMap item = search_text.toMap();
            table->insertRow(i);
            table->setItem(i,  j,initValue(item["text"].toString()));
            i++;
        }
    }

}

void WriteJson(QTableWidget* table)
{
    QFile file;
    int cntRow = table->rowCount();

    file.setFileName("settings.json");
    file.open(QIODevice::WriteOnly);
    QTextStream out(&file);
    //out.setCodec("UTF-8");
    //out.setGenerateByteOrderMark(true);
    QJson::Serializer serializer;
    QVariantList search_texts;
    for (int i=0;i < cntRow;i++){
        QVariantMap search_text;
        search_text.insert("text", table->item(i,0)->text());
        //search_text.insert("urls", table->item(i,1)->text());
        search_texts.push_back(search_text);
    }
    bool ok;

    QVariantMap res;
    res.insert("search_texts",search_texts);
    out << serializer.serialize(res,&ok);
    out.flush();
    file.close();
}

void InsertCol(QTableWidget* table, int index, const QString& txt)
{
    QTableWidgetItem* item = new QTableWidgetItem(txt,QTableWidgetItem::Type);
    table->setHorizontalHeaderItem(index, item);
}

void MainWindow::showEvent(QShowEvent *event)
{
    qDebug() << "Show event";
    QTableWidget* table = (ui->tableWidget);
    table->clear();
    table->setRowCount(0);
    table->setColumnCount(1);

    InsertCol(table, 0,QString("text"));


    /*resize*/
    table->setColumnWidth(0,250+250+260);

    ReadJson(table);
    QMainWindow::showEvent(event);
}


void MainWindow::on_btInsert_clicked()
{
    ui->tableWidget->AddRow();
}

void MainWindow::on_btRemove_clicked()
{
    ui->tableWidget->RemoveRow();
}

void MainWindow::on_btSave_clicked()
{
    WriteJson(ui->tableWidget);
    QMessageBox msgBox;
    msgBox.setIcon(QMessageBox::Information);
    msgBox.setText("Success save");

    msgBox.exec();
}
