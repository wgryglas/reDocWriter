class ErrorViewInterface:
    def show_error(self, text):
        raise NotImplementedError()

    def show_block(self, text):
        """
        :param text: info
        :return: None
        """
        raise NotImplementedError()

    def ask_yes_no(self, text):
        """
        :param text: question
        :return: Boolean answer to yes, no
        """
        raise NotImplementedError()

    def show_and_exit(self, text):
        raise NotImplementedError()

class DialogErrorView(ErrorViewInterface):

    def __init__(self, root_window, application):
        self.root = root_window
        self.app = application

        from pyqode.qt.QtGui import QErrorMessage, QMessageBox
        from pyqode.qt.QtCore import Qt
        self.msg = QMessageBox(root_window)
        self.msg.setWindowModality(Qt.WindowModal)
        self.msg.setIcon(QMessageBox.Critical)

        self.qsn = QMessageBox(root_window)
        self.qsn.setWindowModality(Qt.WindowModal)
        self.qsn.setIcon(QMessageBox.Warning)
        self.qsn.setStandardButtons(QMessageBox.No | QMessageBox.Yes)

    def show_error(self, text):
        self.show_block(text)

    def show_block(self, text):
        self.msg.setText(text)
        self.msg.exec_()

    def show_and_exit(self, text):
        from pyqode.qt.QtGui import QErrorMessage
        QErrorMessage.showMessage(self.root, text)
        self.app.exit()

    def ask_yes_no(self, text):
        from pyqode.qt.QtGui import QMessageBox
        self.qsn.setText(text if text.endswith('?') else "{}?".format(text))
        return self.qsn.exec_() == QMessageBox.Yes

class ConsoleLogger:
    def error(self, text):
        print text

    def question(self, text, value):
        print "Problem encountered, asked {} and user respond {}".format(text, value)

    def exiting(self):
        print "Critical error, application exiting"

class ErrorHandler:
    def __init__(self, view, logger=ConsoleLogger()):
        self._view_ = view
        self._logger_ = logger

    def show(self, text):
        self._logger_.error(text)
        self._view_.show_error(text)

    def ask_yes_no(self, question):
        result = self._view_.ask_yes_no(question)
        self._logger_.question(question, result)
        return result

    def critical_exit_app(self, text):
        self._logger_.error(text)
        self._logger_.exiting()
        self._view_.show_and_exit(text)
