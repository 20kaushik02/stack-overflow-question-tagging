from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import sys, csv, os
import glob
import joblib


from TagPredictor_misc import *
import dill as pickled

vec = open("../models/test_vec.pickle", 'rb')
vectorizer = pickled.load(vec)

count_vec = open("../models/test_count_vec.pickle", 'rb')
count_vectorizer = pickled.load(count_vec)

class TagPredictor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("StackOverflow Tag Predictor")
        self.width = 850
        self.height = 950
        
        self.setMinimumSize(self.width, self.height)
        
        classifierList = glob.glob('../models/*_2_clf.joblib')
        self.classifiers = [joblib.load(clf) for clf in classifierList]
        
        self.linkLabel = QLabel("Link: ")
        self.questionLink = QLineEdit()
        self.questionLink.setMinimumHeight(30)
        
        self.orLabel = QLabel("(or)")
        
        self.textLabel = QLabel("Question: ")
        self.questionText = QTextEdit()
        self.questionText.setMaximumHeight(150)
        self.questionText.setReadOnly(True)
        
        self.predictBtn = QPushButton('Predict')
        self.predictBtn.clicked.connect(self.predictQn)
        
        self.widget = QWidget(self)
        self.widget.setStyleSheet("QLabel{font-size: 10pt;}")
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)
        
        self.layout.addWidget(self.linkLabel, 0, 0)
        self.layout.addWidget(self.questionLink, 0, 1)
        
        #self.layout.addWidget(self.orLabel, 1, 0, 1, 2, Qt.AlignHCenter)
        
        self.layout.addWidget(self.textLabel, 2, 0, Qt.AlignTop)
        self.layout.addWidget(self.questionText, 2, 1, Qt.AlignTop)
        
        self.layout.addWidget(self.predictBtn, 3, 0, 1, 2, Qt.AlignHCenter)
              
        self.htmlRemTab = QTextEdit()
        self.htmlRemTab.setReadOnly(True)
        self.lowerCaseTab = QTextEdit()
        self.lowerCaseTab.setReadOnly(True)
        self.tokenTab = QTextEdit()
        self.tokenTab.setReadOnly(True)
        self.stopWordsTab = QTextEdit()
        self.stopWordsTab.setReadOnly(True)
        self.lemmatizeTab = QTextEdit()
        self.lemmatizeTab.setReadOnly(True)
        
        self.preprocessTabs = VerticalTabWidget()
        self.preprocessTabs.setMaximumHeight(400)
        
        self.preprocessTabs.addTab(self.htmlRemTab, "1. HTML tags Removal")
        self.preprocessTabs.addTab(self.lowerCaseTab, "2. Lowercase Conversion")
        self.preprocessTabs.addTab(self.tokenTab, "3. Tokenization")
        self.preprocessTabs.addTab(self.stopWordsTab, "4. Stopwords Removal")
        self.preprocessTabs.addTab(self.lemmatizeTab, "5. Lemmatization")
        self.layout.addWidget(self.preprocessTabs, 4, 0, 1, 2)
        
        self._createClassifierTable(["Classifier", "Prediction"], classifierList)
        self.classifierTable.setMinimumHeight(300)
        self.layout.addWidget(self.classifierTable, 5, 0, 1, 2, Qt.AlignTop)
        
        self.tagsLabel = QLabel("Predicted Tags: ")
        self.predictedTags = QLineEdit()
        self.predictedTags.setMinimumHeight(30)
        font = self.predictedTags.font()      # lineedit current font
        font.setPointSize(12) 
        self.predictedTags.setFont(font)
        
        self.layout.addWidget(self.tagsLabel, 6, 0)
        self.layout.addWidget(self.predictedTags, 6, 1)
        
        self.setCentralWidget(self.widget)

    def predictQn(self): 
        try:
            qnLink = self.questionLink.text()
            if (qnLink != ""):
                qnTitle, qnBody =  qn_scrape(qnLink)
                questionBox = f"Title:\n{repr(qnTitle)}\n\nBody:\n{repr(qnBody)}"
                self.questionText.setText(questionBox)
            
            qnText = self.questionText.toPlainText()
            if(qnLink == "" and qnText == ""):
                print("empty")
                return
            
            qnTitle, qnBody = html_tags_remove(qnTitle), html_tags_remove(qnBody)
            htmlRemoveBox = f"Title:\n{qnTitle}\n\nBody:\n{qnBody}"
            self.htmlRemTab.setText(htmlRemoveBox)
            
            qnTitle, qnBody = lower_case(qnTitle), lower_case(qnBody)
            lowerCaseBox = f"Title:\n{qnTitle}\n\nBody:\n{qnBody}"
            self.lowerCaseTab.setText(lowerCaseBox)
            
            qnTitle, qnBody = tokenizeText(qnTitle), tokenizeText(qnBody)
            tokenizeBox = f"Title:\n{qnTitle}\n\nBody:\n{qnBody}"
            self.tokenTab.setText(tokenizeBox)
            
            qnTitle, qnBody = filter_stopwords(qnTitle), filter_stopwords(qnBody)
            stopWordsBox = f"Title:\n{qnTitle}\n\nBody:\n{qnBody}"
            self.stopWordsTab.setText(stopWordsBox)
            
            qnTitle, qnBody = lemmatizeText(qnTitle), lemmatizeText(qnBody)
            lemmatizeBox = f"Title:\n{qnTitle}\n\nBody:\n{qnBody}"
            self.lemmatizeTab.setText(lemmatizeBox)
            
            
            X_tfidf = vectorizeQn(" ".join(qnTitle) + " ".join(qnTitle) + " ".join(qnTitle) + " ".join(qnBody))    
            #multilabel_binarizer = joblib.load('../models/count_vectorizer.joblib')
        
            results = set()
            for i, classifier in enumerate(self.classifiers):
                    y_pred = classifier.predict(X_tfidf)
                    preds = list(count_vectorizer.inverse_transform(y_pred)[0])
                    self.classifierTable.setItem(i, 1, QTableWidgetItem(str(preds)))
                    results.update(preds)
            
            self.predictedTags.setText(', '.join(str(tag) for tag in results))
        except:
            pass
        
    def _createClassifierTable(self, headers, classifierList):
        
        self.classifierTable = QTableWidget()
        self.classifierTable.setColumnCount(len(headers))
        self.classifierTable.setHorizontalHeaderLabels(headers)
        self.classifierTable.verticalHeader().setVisible(False)
        self.classifierTable.setTabKeyNavigation(False)
        self.classifierTable.setProperty("showDropIndicator", False)
        self.classifierTable.setDragDropOverwriteMode(False)
        self.classifierTable.setSortingEnabled(False)
        self.classifierTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.classifierTable.setSelectionMode(QAbstractItemView.NoSelection)
        
        self.classifierTable.horizontalHeader(). setSectionResizeMode(1, QHeaderView.Stretch)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classifierTable.sizePolicy().hasHeightForWidth())
        self.classifierTable.setSizePolicy(sizePolicy)
        
        for row, classifierPath in enumerate(classifierList):
            rowpos = self.classifierTable.rowCount()
            self.classifierTable.insertRow(rowpos)
            self.classifierTable.setItem(rowpos, 0, QTableWidgetItem(str(os.path.basename(classifierPath).split("_")[0])))
            
class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QTabWidget.West)


def main():
    app = QApplication(sys.argv)
    aunms = TagPredictor()
    aunms.show()
    app.exec()
    
if __name__ == "__main__":
    main()