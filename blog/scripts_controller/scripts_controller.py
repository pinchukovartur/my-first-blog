import datetime
import os
import signal
import subprocess
import threading
import xml.etree.cElementTree as ET

# install libs
import psutil

# config file location
CONFIG_PATH = os.path.dirname(__file__) + "/xml_data/"


# метод запускающий скрипт
def run_script(script_name, script_type, auth_script, script_path, start_date_script):
    # записываем в конфиг данные скрипта
    config_name = auth_script + ".xml"
    __check_file_exist(CONFIG_PATH + config_name)

    # проверяем тип скрипта
    if script_type == "SINGLE":
        # если скрипт активый кидаем ерор
        if get_script_status(auth_script, script_name):
            raise NameError("ERROR!!! одна копия скрипта уже запущена")
        else:
            __run_script(script_name, auth_script, script_path, CONFIG_PATH, config_name, script_type,
                         start_date_script)
    elif script_type == "MULTI":
        # если мулти
        # запускаем скрипт
        __run_script(script_name, auth_script, script_path, CONFIG_PATH, config_name, script_type, start_date_script)
    else:
        raise NameError("ERROR!!! неизвестный тип скрипта")


# метод записывает информацию о скрипте в xml файл
def _add_script_in_xml(config_path, script_name, script_type, start_date_script, author_script, PID):
    # заполняем
    script = ET.Element("script")
    ET.SubElement(script, "name").text = script_name
    ET.SubElement(script, "type").text = script_type
    ET.SubElement(script, "start_data").text = start_date_script
    ET.SubElement(script, "author").text = author_script
    ET.SubElement(script, "PID").text = PID
    # записываем
    tree = ET.parse(config_path)
    root = tree.getroot()
    root.append(script)
    tree.write(config_path)


# метод создает пустой xml файл если его нет
def __check_file_exist(config_path):
    # если xml файла не существует, то создаем его
    if not os.path.isfile(config_path):
        scripts = ET.Element("scripts")
        tree = ET.ElementTree(scripts)
        tree.write(config_path)


# метод проверяет существует ли папка, если нет то создает ее
def __check_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_script_status(username, script_name):
    __check_file_exist(CONFIG_PATH + username + ".xml")

    # обновляем файл конфигов, 3 раза дабы точно убедиться)))
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")

    # проходим по всем скриптам в конфиге
    tree = ET.parse(CONFIG_PATH + username + ".xml")
    # проходим по всем активным pid-ам
    i = 0
    for scripts in tree.iter():
        if scripts.tag == "scripts":
            for script in scripts:
                for subelem in script:
                    if subelem.tag == "name" and subelem.text == script_name:
                        i = i + 1
                    if subelem.tag == "author" and subelem.text == username:
                        i = i + 1
                    if i > 1:
                        return True

                i = 0
    return False


# the method delete old scripts in xml config
def __delete_old_script_in_xml(config_path):
    # state script in at the time
    state_script = False

    # read xml file
    tree = ET.parse(config_path)
    # bypass scripts
    for scripts in tree.iter():
        if scripts.tag == "scripts":
            # bypass script
            for script in scripts:
                # bypass sub element
                for subelem in script:
                    if subelem.tag == "PID":
                        # bypass on active pids
                        for process in psutil.process_iter():
                            # if script is zombie delete him
                            if str(subelem.text) == str(process.pid) and str(process.status()) == "zombie":
                                state_script = False
                            elif str(subelem.text) == str(process.pid):
                                state_script = True
                # if script was not find delete him
                if not state_script:
                    scripts.remove(script)
                state_script = False
    tree.write(config_path)


def __read_stdout(proc, log_file_name):
    try:
        while True:
            line = proc.stdout.readline().decode("utf-8")
            if line != '':
                f = open(log_file_name, "a")
                f.write(line.rstrip() + "\n")
                f.close()
            else:
                print("finish work process: " + str(proc.pid))
                exit(0)
    except Exception as err:
        print(err)
        exit(404)


# the method create new process
def __run_script(script_name, auth_script, script_path, config_path, config_name, script_type, start_date_script):
    # create path where save logs files
    log_path = os.path.dirname(__file__) + "/logs/" + auth_script + "/"
    # logs name
    log_name = "%" + script_name.replace(" ", "") + "%.txt"
    # check folder if exist create it
    __check_folder(log_path)
    # start process
    log_file_name = log_path + str(datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d_%H_%M_%S_")) + log_name

    process = subprocess.Popen(["/usr/bin/python3.5", script_path], shell=False, stdout=subprocess.PIPE)
    threading._start_new_thread(__read_stdout, (process, log_file_name))

    # add info in xml file with meta data
    _add_script_in_xml(config_path + config_name, script_name, script_type, start_date_script, auth_script,
                       str(process.pid))


# the method stops script
def stop_scripts(username, script_name):
    # проверяем есть ли конфиг у пользователя
    __check_file_exist(CONFIG_PATH + username + ".xml")

    # обновляем файл конфигов, 3 раза дабы точно убедиться)))
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")

    # проходим по всем скриптам в конфиге
    tree = ET.parse(CONFIG_PATH + username + ".xml")
    i = 0
    pid = -1
    for scripts in tree.iter():
        if scripts.tag == "scripts":
            for script in scripts:
                for subelem in script:
                    if subelem.tag == "name" and subelem.text == script_name:
                        i = i + 1
                    if subelem.tag == "author" and subelem.text == username:
                        i = i + 1
                    if subelem.tag == "PID":
                        pid = int(subelem.text)
                        i = i + 1
                    if i > 2 and pid > -1:
                        # УБИВАЕМ ПРОЦЕСС И ЕГО ДЕТЕЙ!!! УХАХААХАХАХАХ насильственно !)
                        os.kill(int(pid), signal.SIGTERM)
                i = 0

    # обновляем файл конфигов, 3 раза дабы точно убедиться)))
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")


def get_count_script_instance(username, script_name):
    __check_file_exist(CONFIG_PATH + username + ".xml")

    # обновляем файл конфигов, 3 раза дабы точно убедиться)))
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")
    __delete_old_script_in_xml(CONFIG_PATH + username + ".xml")

    # проходим по всем скриптам в конфиге
    tree = ET.parse(CONFIG_PATH + username + ".xml")
    # проходим по всем активным pid-ам
    i = 0
    count = 0
    for scripts in tree.iter():
        if scripts.tag == "scripts":
            for script in scripts:
                for subelem in script:
                    if subelem.tag == "name" and subelem.text == script_name:
                        i = i + 1
                    if subelem.tag == "author" and subelem.text == username:
                        i = i + 1
                if i > 1:
                    count = count + 1
                i = 0
    return count
