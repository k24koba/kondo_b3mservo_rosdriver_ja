#!/usr/bin/env python
# -*- coding: utf-8 -*-
# code for python2
import serial
import time
import math
import struct

#シリアルポートをオープン@1.5Mbps。デバイス名は予めシンボリックリンクで固定しておく。
ser = serial.Serial('/dev/Kondo_USB-RS485_converter', 1500000)


# IDが”ID”なサーボの初期化（リセット）
# リセット関数と同じ機能だが、ID0〜255すべてのIDに対して実施することを想定。
# 余計なコンソール出力をなくした他、サーボの有無（＝サーボから返信が来るか否か）で返り値が変わる。
def initServo(ID):
    SUM = (0x08 + 0x04 + 0x00 + ID + 0x02 + 0x28 + 0x01) & 0b11111111 #コマンドの合計値（下位1バイト）を計算
    enFreeServo_command = []
    enFreeServo_command += [chr(0x08), chr(0x04), chr(0x00),
                            chr(ID), chr(0x02), chr(0x28), chr(0x01), chr(SUM)] #コマンドリストにコマンドを格納
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(enFreeServo_command) #コマンド送信
    # print("set servo ID:" + str(ID) + " to FREE mode")
    time.sleep(0.02)  # リセット完了まで待つ

    # サーボが接続されていれば、5バイトの返信が返ってくる。その場合は返り値として１を返す。そうでなければ０を返す。
    if ser.inWaiting() == 5:
        ret = 1
    else:
        ret = 0
    return ret


# IDが”ID”なサーボの初期化（リセット）
# サーボが接続されていなくても挙動が変わらないため注意。
def resetServo(ID):
    SUM = (0x06 + 0x05 + 0x00 + ID + 0x02) & 0b11111111
    resetServo_command = []
    resetServo_command += [chr(0x06), chr(0x05),
                           chr(0x00), chr(ID), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(resetServo_command)
    time.sleep(0.5)  # 返信が来るまで待つ
    print("Reset servo ID:" + str(ID))


# IDが”ID”なサーボをフリーにする関数。
def enFreeServo(ID):
    SUM = (0x08 + 0x04 + 0x00 + ID + 0x02 + 0x28 + 0x01) & 0b11111111
    enFreeServo_command = []
    enFreeServo_command += [chr(0x08), chr(0x04), chr(0x00),
                            chr(ID), chr(0x02), chr(0x28), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(enFreeServo_command)
    time.sleep(0.5)  # wait until this process done
    print("set servo ID:" + str(ID) + " to FREE mode")


# IDが"ID"なサーボを位置制御モード、スタンバイにする関数（軌道生成：別途指定、　制御ゲイン：プリセット#0）
# mode : 00>positionCTRL, 04>velocityCTRL, 08>current(torque)CTRL, 12>feedforwardCTRL
def change_servocontrol_mode(ID, mode):
    SUM = (0x08 + 0x04 + 0x00 + ID + mode + 0x28 + 0x01) & 0b11111111
    change_servocontrol_mode_command = []
    change_servocontrol_mode_command += [chr(0x08), chr(0x04), chr(
        0x00), chr(ID), chr(mode), chr(0x28), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(change_servocontrol_mode_command)
    time.sleep(0.1)  # wait until this process done
    if mode == 0:
        set_servo_gain_to_presets(ID, mode)
        print("set servo ID:" + str(ID) +
              " to position control mode with preset gain #0")
    elif mode == 4:
        set_servo_gain_to_presets(ID, mode)
        print("set servo ID:" + str(ID) +
              " to velocity control mode with preset gain #1")
    elif mode == 8:
        set_servo_gain_to_presets(ID, mode)
        print("set servo ID:" + str(ID) +
              " to current(torque) control mode with preset gain #2")
    elif mode == 12:
        print("set servo ID:" + str(ID) + " to feed-forward control mode")


# IDが"ID"なサーボの位置制御モード時の軌道生成を5-polyモードにする関数
def set_servo_trajectory_to_5Poly(ID):
    SUM = (0x08 + 0x04 + 0x00 + ID + 0x05 + 0x29 + 0x01) & 0b11111111
    set_servo_trajectory_to_5Poly_command = []
    set_servo_trajectory_to_5Poly_command += [chr(0x08), chr(0x04), chr(
        0x00), chr(ID), chr(0x05), chr(0x29), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(set_servo_trajectory_to_5Poly_command)
    time.sleep(0.1)  # wait until this process done
    print("set servo ID:" + str(ID) + " to 5-poly Trajectory")


# IDが"ID"なサーボの位置制御モード時の軌道生成をEVENモード（等速）にする関数
def set_servo_trajectory_to_EVEN(ID):
    SUM = (0x08 + 0x04 + 0x00 + ID + 0x01 + 0x29 + 0x01) & 0b11111111
    set_servo_trajectory_to_EVEN_command = []
    set_servo_trajectory_to_EVEN_command += [chr(0x08), chr(0x04), chr(
        0x00), chr(ID), chr(0x01), chr(0x29), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(set_servo_trajectory_to_EVEN_command)
    time.sleep(0.1)  # wait until this process done
    print("set servo ID:" + str(ID) + " to Even Trajectroy")


# IDが"ID"なサーボの制御ゲインをプリセットのものに設定する関数
# プリセット0:位置制御用、1:速度制御用、2:トルク制御用
def set_servo_gain_to_presets(ID, PresetNumber):
    ser.reset_input_buffer()  # 返信データを読み取ってバッファから消しておく
    SUM = (0x08 + 0x04 + 0x00 + ID + PresetNumber + 0x5c + 0x01) & 0b11111111
    set_servo_gain_to_presets_command = []
    set_servo_gain_to_presets_command += [chr(0x08), chr(0x04), chr(
        0x00), chr(ID), chr(PresetNumber), chr(0x5c), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(set_servo_gain_to_presets_command)
    time.sleep(0.1)  # wait until this process done


# IDが"ID"なサーボの位置を、目標時間"Time(ms)"をかけて"Angle(/100 deg)"にセットする関数
def control_servo_by_position_with_time(ID, Angle_centDeg, Time_msec):
    ser.reset_input_buffer()  # 返信データを読み取ってバッファから消しておく
    if Angle_centDeg < 0:  # 目標角度が負の場合、-1→65535(0xffff)、-32000→33536(0x8300)と変換
        modAngle = 65536 + Angle_centDeg
    else:
        modAngle = Angle_centDeg

    SUM = (0x09 + 0x06 + 0x00 + ID + (modAngle & 0xff) + (modAngle
                                                          >> 8) + (Time_msec & 0xff) + (Time_msec >> 8)) & 0b11111111
    control_servo_by_position_with_time_command = []
    control_servo_by_position_with_time_command += [chr(0x09), chr(0x06), chr(0x00), chr(ID), chr(
        modAngle & 0xff), chr(modAngle >> 8), chr(Time_msec & 0xff), chr(Time_msec >> 8), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(control_servo_by_position_with_time_command)
    time.sleep(1.0 * Time_msec / 1000)
    print("set servo ID:" + str(ID) + " to position " +
          str(Angle_centDeg / 100) + "[deg] by " + str(Time_msec) + "[ms]")


# IDが"ID"なサーボの位置を"Angle(/100 deg)"にセットする関数、余裕時間として"Time[ms]"を見ておく
# 軌道生成を行わないので急峻な動きになる。
# 移動に要する時間は関数呼び出し側で確保する必要あり。
def control_servo_by_position_without_time(ID, Angle_centDeg):
    if Angle_centDeg < 0:  # 目標角度が負の場合、-1→65535(0xffff)、-32000→33536(0x8300)と変換
        modAngle = 65536 + Angle_centDeg
    else:  # 目標角度が正の場合でも、コンソールにAngle値を表示したいので、信号送信用の変数はmodAngleとする
        modAngle = Angle_centDeg

    SUM = (0x09 + 0x04 + 0x00 + ID + (modAngle & 0xff) +
           (modAngle >> 8) + 0x2A + 0x01) & 0b11111111
    control_servo_by_position_without_time_command = []
    control_servo_by_position_without_time_command += [chr(0x09), chr(0x04), chr(0x00), chr(
        ID), chr(modAngle & 0xff), chr(modAngle >> 8), chr(0x2A), chr(0x01), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(control_servo_by_position_without_time_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 5:
            ser.reset_input_buffer()  # 返信データを読み取ってバッファから消しておく
            break

    # 結果を出力したい場合は以下をアクティベート
    # print("set servo ID:" + str(ID) + " to position " +
    #       str(Angle_centDeg / 100.0) + "[deg]")


def control_servo_by_Velocity(ID, Velocity_centDeg_perSec):  # 速度(100*deg/sec)
    # 目標角度が負の場合、-1→65535(0xffff)、-32000→33536(0x8300)と変換
    if Velocity_centDeg_perSec < 0:
        modVelocity = 65536 + Velocity_centDeg_perSec
    else:  # 目標角度が正の場合でも、コンソールにAngle値を表示したいので、信号送信用の変数はmodAngleとする
        modVelocity = Velocity_centDeg_perSec

    SUM = (0x09 + 0x04 + 0x00 + ID + (modVelocity & 0xff) +
           (modVelocity >> 8) + 0x30 + 0x01) & 0b11111111
    control_servo_by_Velocity_command = []
    control_servo_by_Velocity_command += [chr(0x09), chr(0x04), chr(0x00), chr(ID), chr(
        modVelocity & 0xff), chr(modVelocity >> 8), chr(0x30), chr(0x01), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(control_servo_by_Velocity_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 5:
            ser.reset_input_buffer()  # 返信データを読み取ってバッファから消しておく
            break

    # 結果を出力したい場合は以下をアクティベート
    # print("set servo ID:" + str(ID) + " to Velocity " +
    #       str(Velocity_centDeg_perSec / 100.0) + "[deg/sec]")


# IDが"ID"なサーボの目標トルクを"Torque(mNm)"にセットする関数
def control_servo_by_Torque(ID, Torque_mNm):
    # now = time.time()
    if Torque_mNm < 0:  # 目標トルクが負の場合、-1→65535(0xffff)、-32000→33536(0x8300)と変換
        modTorque = 65536 + Torque_mNm
    else:  # 目標トルクが正の場合でも、コンソールにTorque値を表示したいので、信号送信用の変数はmodTorqueとする
        modTorque = Torque_mNm
    SUM = (0x09 + 0x04 + 0x00 + ID + (modTorque & 0xff) +
           (modTorque >> 8) + 0x3c + 0x01) & 0b11111111
    control_servo_by_Torque_command = []
    control_servo_by_Torque_command += [chr(0x09), chr(0x04), chr(0x00), chr(
        ID), chr(modTorque & 0xff), chr(modTorque >> 8), chr(0x3c), chr(0x01), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(control_servo_by_Torque_command)

    # wait until reply will come
    while True:
        if ser.inWaiting() == 5:
            ser.reset_input_buffer()  # 返信データを読み取ってバッファから消しておく
            break
    # time.sleep(0.012)
    # dt = time.time() - now
    # print(dt)
    # print("")

    # 結果を出力したい場合は以下をアクティベート
    # print results
    # print("set servo ID:" + str(ID)
    #       + " to Torque " + str(Torque_mNm) + "[mNm]")


def control_servo_by_Torque_multicast(args):
    length = len(args) / 2
    id = []
    torque_command = []
    id_sum = 0
    torque_command_sum = 0
    for i in range(length):
        id.append(args[i])
        torque_command.append(args[i + length])
        if torque_command[i] < 0:
            torque_command[i] = 65536 + torque_command[i]
        id_sum = id_sum + id[i]
        torque_command_sum = torque_command_sum + \
            (torque_command[i] & 0xff) + (torque_command[i] >> 8)

    # print(torque_command)
    # print("")
    command_length = (3 + 3 * length + 3) & 0b11111111
    SUM = (command_length + 0x04 + 0x00 + id_sum +
           torque_command_sum + 0x3c + length) & 0b11111111

    control_servo_by_Torque_multicast_command = []
    control_servo_by_Torque_multicast_command += [
        chr(command_length), chr(0x04), chr(0x00)]
    for j in range(length):
        control_servo_by_Torque_multicast_command += [
            chr(id[j]), chr(torque_command[j] & 0xff), chr(torque_command[j] >> 8)]
    control_servo_by_Torque_multicast_command += [
        chr(0x3c), chr(length), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(control_servo_by_Torque_multicast_command)
    time.sleep(0.005) # マルチキャストの場合返信が無いため、一定時間待つ。
    args = []


# test comments
# IDが"ID"なサーボの角度取得
def get_servo_Position(ID):
    # アドレス0x2cから2バイト分（=角度）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x2c + 0x02) & 0b11111111
    get_servo_Position_command = []
    get_servo_Position_command += [chr(0x07), chr(0x03),
                                   chr(0x00), chr(ID), chr(0x2c), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_servo_Position_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信を処理。最初の４バイトは共通なので、適当な変数に格納しておく。次の２バイトが角度なので、受信し、リトルエンディアンで整数に変換。
    Receive = ser.read(4)
    Angle1 = ser.read(1)
    Angle2 = ser.read(1)
    intAngle1 = ord(Angle1)
    intAngle2 = ord(Angle2)

    Angle = (intAngle2 << 8) | intAngle1

    # 角度が正の場合は角度*100の値が表示されるが、負の場合は違うので、そこを処理
    if Angle > 0x8300:
        Angle = Angle - 0x10000

    # 角度を返す
    # print(str(Angle / 100.0) + "[deg]")
    ser.reset_input_buffer()
    return Angle


# IDが"ID"なサーボの速度取得
def get_servo_Velocity(ID):
    # アドレス0x2cから2バイト分（=角度）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x32 + 0x02) & 0b11111111
    get_servo_Velocity_command = []
    get_servo_Velocity_command += [chr(0x07), chr(0x03),
                                   chr(0x00), chr(ID), chr(0x32), chr(0x02), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_servo_Velocity_command)
    # 返信（７バイト）がくるまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが速度のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    Velocity1 = ser.read(1)
    Velocity2 = ser.read(1)
    intVelocity1 = ord(Velocity1)
    intVelocity2 = ord(Velocity2)

    Velocity = (intVelocity2 << 8) | intVelocity1

    # 角度が正の場合は角度*100の値が表示されるが、負の場合は違うので、そこを処理
    if Velocity > 0x8300:
        Velocity = Velocity - 0x10000

    # 角度を返す
    # print(str(Velocity / 100.0) + "[deg/sec]")
    ser.reset_input_buffer()
    return Velocity


# IDが”ID"なサーボの電流値を取得する関数
def get_servo_Current(ID):
    # アドレス0x48から2バイト分（=電流値）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x48 + 0x02) & 0b11111111
    get_servo_Current_command = []
    get_servo_Current_command += [chr(0x07), chr(0x03),
                                  chr(0x00), chr(ID), chr(0x48), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_servo_Current_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが電流値のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    Current1 = ser.read(1)
    Current2 = ser.read(1)
    intCurrent1 = ord(Current1)
    intCurrent2 = ord(Current2)
    Current = (intCurrent2 << 8) | intCurrent1

    # 電流値が正の場合はその値が表示されるが、負の場合は違うので、そこを処理
    if Current > 0x8300:
        Current = Current - 0x10000

    # return current
    # print(str(Current) + " [mA]")
    return Current


# IDが”ID"なサーボの印加電圧（＝バッテリ電圧）を取得する関数
def get_servo_voltage(ID):
    # アドレス0x4aから2バイト分（=電流値）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x4a + 0x02) & 0b11111111
    get_servo_voltage_command = []
    get_servo_voltage_command += [chr(0x07), chr(0x03),
                                  chr(0x00), chr(ID), chr(0x4a), chr(0x02), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_servo_voltage_command)
    # wait until receive the data (3 bytes at minimum)
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが電流値のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    voltage1 = ser.read(1)
    voltage2 = ser.read(1)
    int_voltage1 = ord(voltage1)
    int_voltage2 = ord(voltage2)
    voltage = (int_voltage2 << 8) | int_voltage1

    # return voltage
    # print(str(voltage) + " [mV]")
    return voltage


# IDが”ID"なサーボのMCU温度を取得する関数
def get_mcu_temperature(ID):
    # アドレス0x44から2バイト分（=電流値）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x44 + 0x02) & 0b11111111
    get_mcu_temperature_command = []
    get_mcu_temperature_command += [chr(0x07), chr(0x03),
                                    chr(0x00), chr(ID), chr(0x44), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_mcu_temperature_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが温度情報のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    mcu_temperature1 = ser.read(1)
    mcu_temperature2 = ser.read(1)
    int_mcu_temperature1 = ord(mcu_temperature1)
    int_mcu_temperature2 = ord(mcu_temperature2)
    mcu_temperature = (int_mcu_temperature2 << 8) | int_mcu_temperature1

    # 温度が正の場合はその値が表示されるが、負の場合は違うので、そこを処理
    if mcu_temperature > 0x8300:
        mcu_temperature = mcu_temperature - 0x10000

    # return mcu_temperature
    mcu_temperature = mcu_temperature / 100.0
    print(str(mcu_temperature) + " [degree_celcius]")
    return mcu_temperature


# IDが”ID"なサーボの本体温度を取得する関数
def get_servo_temperature(ID):
    # アドレス0x46から2バイト分（=電流値）読みだす信号を作成し、送信
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x46 + 0x02) & 0b11111111
    get_servo_temperature_command = []
    get_servo_temperature_command += [chr(0x07), chr(0x03),
                                      chr(0x00), chr(ID), chr(0x46), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_servo_temperature_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが温度情報のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    servo_temperature1 = ser.read(1)
    servo_temperature2 = ser.read(1)
    int_servo_temperature1 = ord(servo_temperature1)
    int_servo_temperature2 = ord(servo_temperature2)
    servo_temperature = (int_servo_temperature2 << 8) | int_servo_temperature1

    # ondoが正の場合はその値が表示されるが、負の場合は違うので、そこを処理
    if servo_temperature > 0x8300:
        servo_temperature = servo_temperature - 0x10000

    # return mcu_temperature
    servo_temperature = servo_temperature / 100.0
    print(str(servo_temperature) + " [degree_celcius]")
    return servo_temperature


# IDが”ID"なサーボのエンコーダカウントをリセットする関数
def reset_encoder_total_count(ID):
    SUM = (0x0B + 0x04 + 0x00 + ID + 0x00 + 0x00 +
           0x00 + 0x00 + 0x52 + 0x01) & 0b11111111
    reset_encoder_total_count_command = []
    reset_encoder_total_count_command += [chr(0x0B), chr(0x04), chr(0x00), chr(
        ID), chr(0x00), chr(0x00), chr(0x00), chr(0x00), chr(0x52), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(reset_encoder_total_count_command)
    time.sleep(0.1)  # wait until this process done
    print("finished resetting encoder")


# IDが”ID"なサーボのエンコーダカウントを取得する関数
def get_encoder_total_count(ID):
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x52 + 0x04) & 0b11111111
    get_encoder_total_count_command = []
    get_encoder_total_count_command += [chr(0x07), chr(
        0x03), chr(0x00), chr(ID), chr(0x52), chr(0x04), chr(SUM)]

    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(get_encoder_total_count_command)
    now = time.time()
    # # wait until receive the data (4 bytes at minimum)
    while True:
        if ser.inWaiting() == 9:
            break
    dt = time.time() - now
    # print(dt)
    # print("")

    # process the reply from servo. first 4 bytes is general information, so you can discard it.
    # next 4 bytes are encoder count, so get them and merge by little endian
    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の４バイトがエンコーダカウントのため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    EncoderCount1 = ser.read(1)
    EncoderCount2 = ser.read(1)
    EncoderCount3 = ser.read(1)
    EncoderCount4 = ser.read(1)

    EncoderCount1 = ord(EncoderCount1)
    EncoderCount2 = ord(EncoderCount2)
    EncoderCount3 = ord(EncoderCount3)
    EncoderCount4 = ord(EncoderCount4)

    EncoderCount = (EncoderCount4 << 24) | (EncoderCount3
                                            << 16) | (EncoderCount2 << 8) | EncoderCount1
    if EncoderCount >= 2147483648:
        EncoderCount = EncoderCount - 4294967296
    # カウント値を返す
    # print(str(EncoderCount) + "[count]")
    return EncoderCount


# IDが”ID"なサーボの電流値リミットを変更する関数
def change_current_limit(ID, current_limit_mA):
    SUM = (0x09 + 0x04 + 0x00 + ID + (current_limit_mA & 0xff) +
           (current_limit_mA >> 8) + 0x11 + 0x01) & 0b11111111
    change_current_limit_command = []
    change_current_limit_command += [chr(0x09), chr(0x04), chr(0x00), chr(ID), chr(
        current_limit_mA & 0xff), chr(current_limit_mA >> 8), chr(0x11), chr(0x01), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(change_current_limit_command)
    time.sleep(0.1)

    # 電流値リミット値を読み取り、変更の結果を確認する。
    current_limit = read_current_limit(ID)
    print("set current limit of servo ID: " +
          str(ID) + " as " + str(current_limit) + "[mA]")


# IDが”ID"なサーボの電流値リミットを取得する関数
def read_current_limit(ID):
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x11 + 0x02) & 0b11111111
    read_current_limit_command = []
    read_current_limit_command += [chr(0x07), chr(0x03),
                                   chr(0x00), chr(ID), chr(0x11), chr(0x02), chr(SUM)]
    ser.reset_input_buffer()  # サーボからの返信に備えてシリアル受信バッファをクリア
    ser.write(read_current_limit_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 7:
            break

    # 返信の処理。最初の４バイトは共通なのでバッファから読み取って適当な変数に格納するのみ。
    # 次の２バイトが電流値リミット情報のため、１バイトずつ読み取ってリトルエンディアンで結合する。
    Receive = ser.read(4)
    current_limit1 = ser.read(1)
    current_limit2 = ser.read(1)
    current_limit1 = ord(current_limit1)
    current_limit2 = ord(current_limit2)

    current_limit = (current_limit2 << 8) | current_limit1
    print("current limit of servo ID: " + str(ID) +
          " is " + str(current_limit) + "[mA]")
    return current_limit


def read_time_for_determine_that_servo_is_locked(ID):

    ser.reset_input_buffer()
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x14 + 0x01) & 0b11111111
    read_servo_lock_time_command = []
    read_servo_lock_time_command += [chr(0x07), chr(0x03),
                                     chr(0x00), chr(ID), chr(0x14), chr(0x01), chr(SUM)]
    ser.write(read_servo_lock_time_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 6:
            break

    Receive = ser.read(4)
    lock_time = ser.read(1)
    int_lock_time = ord(lock_time)

    print("lock time of servo ID: " + str(ID) +
          " is " + str(int_lock_time) + " [mSec]")
    return int_lock_time


def read_servo_output_to_countup_time_to_determine_that_servo_is_locked(ID):

    ser.reset_input_buffer()
    SUM = (0x07 + 0x03 + 0x00 + ID + 0x15 + 0x01) & 0b11111111
    read_servo_lock_output_command = []
    read_servo_lock_output_command += [chr(0x07), chr(0x03),
                                       chr(0x00), chr(ID), chr(0x15), chr(0x01), chr(SUM)]
    ser.write(read_servo_lock_output_command)
    # 通信が来るまで待つ
    while True:
        if ser.inWaiting() == 6:
            break

    Receive = ser.read(4)
    lock_output = ser.read(1)
    int_lock_output = ord(lock_output)

    print("lock output of servo ID: " + str(ID) +
          " is " + str(int_lock_output) + " [%]")
    return int_lock_output


def save_RAM_to_ROM(ID):

    SUM = (0x05 + 0x02 + 0x00 + ID) & 0b11111111
    save_RAM_to_ROM_command = []
    save_RAM_to_ROM_command += [chr(0x05),
                                chr(0x02), chr(0x00), chr(ID), chr(SUM)]
    ser.write(save_RAM_to_ROM_command)
    time.sleep(0.1)
    print("save parameters to ROM of servo ID: " + str(ID))


"""
# IDが"ID"なサーボのトルク制御（角度フィードバック, 目標角度"goal_Angle"）
def Trq_by_Ang(ID, goal_Angle):
	# トルクゲインを決定
	Kp = 0.2	#比例ゲイン
	Ki = 0.3	#積分ゲイン
	Kd = 0.3	#微分ゲイン
	count = 10	#トルクの立ち上がりを穏やかにする係数（その１）
	count2 = 0	#トルクの立ち上がりを穏やかにする係数（その２、穏やかさが長続きするように）
	count3 = 0	#制御終了判定をするための変数
	count4 = 0	#offsetをキャンセルする場合に使う変数（積分制御用）
	current_Angle = readServoPOS(ID)
	previous_Angle = current_Angle
	offset = 0	#累積角度誤差（積分制御用）
	current_time = time.time()	#実行時間（角度フィードバックトルク制御の開始時点）
	previous_time = current_time
	Torque_MAX = 700	#目標トルクの最大値を規定（mNm)

	while(True):
		# トルクの立ち上がりを穏やかにする変数の処理
		count2 = count / 10
		count += 1

		# 一定周期ごとに積分制御用の累積角度誤差をゼロにする（外乱を受けつつ一定角度に保持するような場合に発散してしまうので）
		# count4 += 1
		if count4 == 100:
			offset = 0
			count4 = 0

		# 現在角度を取得
		previous_Angle = current_Angle
		current_Angle = readServoPOS(ID)

		# 位置オフセットを積分により取得
		previous_time = current_time
		current_time = time.time()
		dt = current_time - previous_time
		if math.fabs(goal_Angle - current_Angle) < 500:
			offset += (goal_Angle - current_Angle) * dt

		# 目標角度との差分に応じたトルクを発揮（PID制御）
		Torque = (goal_Angle - current_Angle)*Kp + (previous_Angle - current_Angle)*Kd + offset * Ki

		# そもそもトルクが大きすぎるとサーボに負荷がかかるので、制限する。
		if Torque > Torque_MAX:
			Torque = Torque_MAX
		if Torque < -1 * Torque_MAX:
			Torque = -1 * Torque_MAX

		# トルクの立ち上がりを穏やかにする係数をかける
		# トルクは整数しか受け取れないので、変換
		Torque = Torque * (1 - (1 / count2))
		Torque = int(Torque)


		# 目標トルク値をコンソールに出力しつつ、実際にトルク制御
		# print(str(current_Angle/100) + '[deg], ' + str(Torque) + '[mNm]')
		# print(count2)
		# print(offset)
		setTRQ(ID, Torque)
		time.sleep(0.002)

		# 角度誤差が一定以下の時間が一定期間続いたら、制御終了
		if math.fabs(goal_Angle - current_Angle) < 100:	#単位：[/100 deg]
			count3 += 1
			if count3 > 10:
				setTRQ(ID, 0)	#トルクをゼロにして制御をやめる。
				break
	print("end of Positioning by Torque Ctrl")
"""


"""
# IDが"ID"なサーボをトルク制御モードにする関数（制御ゲイン：プリセット#2）
def set_servo_to_TorqueCtrlMode(ID):
	set_servo_gain_to_presets(ID, 2)
	SUM = (0x08 + 0x04 + 0x00 + ID + 0x08 + 0x28 + 0x01) & 0b11111111
	set_servo_to_TorqueCtrlMode_command = []
	set_servo_to_TorqueCtrlMode_command += [chr(0x08), chr(0x04), chr(0x00), chr(ID), chr(0x08), chr(0x28), chr(0x01), chr(SUM)]
	ser.write(set_servo_to_TorqueCtrlMode_command)
	time.sleep(0.0001) #wait until this process done
	print("set servo ID:" + str(ID) + " to Trq Ctrl mode, Gain:preset#2")
"""

"""
# IDが"ID"なサーボのトルク制御（角度フィードバック, 目標角度"goal_Angle"）、無限ループなし（実質P制御）
def Trq_by_Ang(ID, goal_Angle):
    # トルクゲインを決定
    Kp = 0.2  # 比例ゲイン
    Ki = 0.0  # 積分ゲイン
    Kd = 0.0  # 微分ゲイン
    count = 10  # トルクの立ち上がりを穏やかにする係数（その１）
    count2 = 0  # トルクの立ち上がりを穏やかにする係数（その２、穏やかさが長続きするように）
    count3 = 0  # 制御終了判定をするための変数
    count4 = 0  # offsetをキャンセルする場合に使う変数（積分制御用）
    current_Angle = readServoPOS(ID)
    previous_Angle = current_Angle
    offset = 0  # 累積角度誤差（積分制御用）
    current_time = time.time()  # 実行時間（角度フィードバックトルク制御の開始時点）
    previous_time = current_time
    Torque_MAX = 700  # 目標トルクの最大値を規定（mNm)

    # トルクの立ち上がりを穏やかにする変数の処理
    count2 = count / 10
    count += 1

    # 一定周期ごとに積分制御用の累積角度誤差をゼロにする（外乱を受けつつ一定角度に保持するような場合に発散してしまうので）
    # count4 += 1
    if count4 == 100:
        offset = 0
        count4 = 0

    # 現在角度を取得
    previous_Angle = current_Angle
    current_Angle = readServoPOS(ID)
    # 位置オフセットを積分により取得
    previous_time = current_time
    current_time = time.time()
    dt = current_time - previous_time
    if math.fabs(goal_Angle - current_Angle) < 500:
        offset += goal_Angle - current_Angle

    # 目標角度との差分に応じたトルクを発揮（PID制御）
    Torque = (goal_Angle - current_Angle) * Kp + \
        (previous_Angle - current_Angle) * Kd + offset * Ki * dt

    # そもそもトルクが大きすぎるとサーボに負荷がかかるので、制限する。
    if Torque > Torque_MAX:
        Torque = Torque_MAX
    if Torque < -1 * Torque_MAX:
        Torque = -1 * Torque_MAX

    # トルクの立ち上がりを穏やかにする係数をかける
    # トルクは整数しか受け取れないので、変換
    # Torque = Torque * (1 - (1 / count2))
    Torque = int(Torque)

    # 目標トルク値をコンソールに出力しつつ、実際にトルク制御
    print(str(current_Angle / 100) + '[deg], ' + str(Torque) + '[mNm]')
    # print(count2)
    # print(offset)
    setTRQ(ID, Torque)
    time.sleep(0.002)

    # 角度誤差が一定以下の時間が一定期間続いたら、制御終了
    if math.fabs(goal_Angle - current_Angle) < 100:  # 単位：[/100 deg]
        count3 += 1
        if count3 > 10:
            setTRQ(ID, 0)  # トルクをゼロにして制御をやめる。
    # print("end of Positioning by Torque Ctrl")
"""
