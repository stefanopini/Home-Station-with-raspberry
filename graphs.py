from PyQt5 import QtCore, QtGui
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class ThreadGraphs(QtCore.QThread):

    signal_minmax = QtCore.pyqtSignal()

    def __init__(self, window, cursor, connection, reload_seconds_sampling, reload_seconds):
        QtCore.QThread.__init__(self)
        self.window = window
        self.cursor = cursor
        self.reload_seconds_sampling = reload_seconds_sampling
        self.connection = connection
        self.reload_seconds = reload_seconds

        self.temp_min = None
        self.temp_max = None
        self.humi_min = None
        self.humi_max = None
        self.pixmap_pres = None

        self.cursor.execute("DELETE FROM BME_280")
        self.connection.commit()

    def __del__(self):
        self.wait()

    def run(self):
        self.get_data_from_db()

    def get_data_from_db(self):

        while True:

            data_fetched = False

            try:
                seconds_in_a_day = 86400
                limit_number = int(seconds_in_a_day / self.reload_seconds_sampling)

                self.cursor.execute("SELECT * FROM BME_280 ORDER BY CREATED DESC")
                records = self.cursor.fetchall()

                records_np = np.array(records)

                # print("len", len(records_np))
                if len(records_np) > 0:
                    data_fetched = True
                    records_np = np.flipud(records_np)

                    array_temp = (np.array(records_np[:, 0], dtype=np.float))
                    array_pres = (np.array(records_np[:, 1], dtype=np.float))
                    array_humi = (np.array(records_np[:, 2], dtype=np.float))

                    self.temp_min = np.min(array_temp)
                    self.temp_max = np.max(array_temp)

                    self.humi_min = np.min(array_humi)
                    self.humi_max = np.max(array_humi)

                    # self.window.lcd_min_temp.display()
                    # self.window.lcd_max_temp.display()

                    # self.window.lcd_min_humi.display()
                    # self.window.lcd_max_humi.display()

                    index_min_press = np.argmin(array_pres)
                    index_max_press = np.argmax(array_pres)

                    if index_max_press > index_min_press:
                        self.pixmap_pres = QtGui.QPixmap('./icons/arrow_up.png')
                        # self.window.arrow_press.setScaledContents(True)
                        # self.window.arrow_press.setPixmap(pixmap)
                    else:
                        self.pixmap_pres = QtGui.QPixmap('./icons/arrow_down.png')
                        # self.window.arrow_press.setScaledContents(True)
                        # self.window.arrow_press.setPixmap(pixmap)

                    self.signal_minmax.emit()

                    if len(records_np) > limit_number:
                        print("Deleting rows...")
                        date_to_delete = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
                        # delete rows of yesterday
                        self.cursor.execute("DELETE FROM BME_280 WHERE CREATED < '{}';".format(date_to_delete))
                        self.connection.commit()
                        print("Total rows deleted: %d" % self.cursor.rowcount)


            except Exception as e:
                print("Error: loading DB values: ", e)

            try:
                ###

                if data_fetched:
                    if len(array_temp) > 5:
                        step = int(len(array_temp)/5)
                    else:
                        step = 1

                    plt.plot(array_temp)
                    plt.box(False)
                    plt.grid()

                    # plt.rcParams.update({'font.size': 50})
                    plt.xticks(np.arange(0, len(array_temp), step))
                    plt.yticks(np.arange(10, 30, 2))

                    plt.savefig("graphs/temp.png", bbox_inches='tight')

                    plt.cla()
                    plt.clf()
                    plt.close()

                    ###

                    plt.plot(array_humi)
                    plt.box(False)
                    plt.grid()

                    # plt.rcParams.update({'font.size': 50})
                    plt.xticks(np.arange(0, len(array_temp), step))
                    # plt.yticks(np.arange(10, 30, 2))

                    plt.savefig("graphs/humi.png", bbox_inches='tight')
                    plt.cla()
                    plt.clf()
                    plt.close()

                    ###

                    plt.plot(array_pres)
                    plt.box(False)
                    plt.grid()

                    # plt.rcParams.update({'font.size': 50})
                    plt.xticks(np.arange(0, len(array_temp), step))
                    # plt.yticks(np.arange(10, 30, 2))

                    plt.savefig("graphs/pres.png", bbox_inches='tight')
                    plt.cla()
                    plt.clf()
                    plt.close()


                    # for r in records:
                    #     print(r)

                    # self.s_temp_chart.emit(t, array_temp)
                    # self.s_pres_chart.emit(t, array_pres)
                    # self.s_humi_chart.emit(t, array_humi)

                else:
                    print("Plots not yet enabled...")

            except Exception as e:
                print("Error in plotting values: ", e)

            sleep(self.reload_seconds)


if __name__ == "__main__":
    pass