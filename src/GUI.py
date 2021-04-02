from tkinter import *
from tkinter import scrolledtext
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter
import serial
import threading
import time
import os

def displayInfo():
    j=0
    while True:
        line = ser.readline().strip()
        info = line.decode('ascii')
        count=0

        cTemp=""
        for i in range(1, len(info)):
            if (info[i] == 'P'):
                count=i
                break
            cTemp+=info[i]
        tempArr.append(cTemp)
        
        output.insert(END, "The current temperature in Celsius is: ")
        output.insert(END, cTemp)
        output.insert(END, "\n")
        
        cpH=""
        for i in range(count+1, len(info)):
            if (info[i] == 'S'):
                count=i
                break
            cpH+=info[i]
        phArr.append(cpH)
            
        output.insert(END, "The current pH is: ")
        output.insert(END, cpH)
        output.insert(END, "\n")
        
        cSpeed=""
        for i in range(count+1, len(info)):
            cSpeed+=info[i]
        speedArr.append(cSpeed)
        
        output.insert(END, "The current speed is: ")
        output.insert(END, cSpeed)
        output.insert(END, "\n\n")
        
        if j==0:
            t2 = threading.Thread(target = plot2)
            t2.daemon = True
            t2.start()
            t3 = threading.Thread(target = plot3)
            t3.daemon = True
            t3.start()
            t4 = threading.Thread(target = plot4)
            t4.daemon = True
            t4.start()
        j=1

def plot2():
    root = Tk()
    root.geometry('1500x500')
    root.title('Live pH Plot')
    root.config(background='white')

    xar = []
    yar = []

    style.use('ggplot')
    fig = plt.figure(figsize=(14, 4.5), dpi=100)
    ax1 = fig.add_subplot(1, 1, 1)
    line, = ax1.plot(xar, yar, 'r', marker='o', label="pH Plot")
    ax1.set_xlabel("Number of reading")
    ax1.set_ylabel("pH Value")
    legend = ax1.legend(loc='upper right')
    def animate(i):
        if float(phArr[len(phArr)-1])!=float(phArr[len(phArr)-2]):
            yar.append(float(phArr[len(phArr)-1]))
            xar.append(i)
            line.set_data(xar, yar)
            ax1.set_xlim(0, i+1)
            ax1.set_ylim(2, 8)


    plotcanvas = FigureCanvasTkAgg(fig, root)
    plotcanvas.get_tk_widget().grid(column=1, row=1)
    ani = animation.FuncAnimation(fig, animate, interval=15000, blit=False)
    root.mainloop()

def plot3():
    root = Tk()
    root.geometry('1500x500')
    root.title('Live Stirring Speed Plot')
    root.config(background='white')

    xar = []
    yar = []

    style.use('ggplot')
    fig = plt.figure(figsize=(14, 4.5), dpi=100)
    ax1 = fig.add_subplot(1, 1, 1)
    line, = ax1.plot(xar, yar, 'g', marker='o', label="RPM Plot")
    ax1.set_xlabel("Number of reading")
    ax1.set_ylabel("Stirring Speed in RPM")
    legend = ax1.legend(loc='upper right')
    def animate(i):
        if float(speedArr[len(speedArr)-1])!=float(speedArr[len(speedArr)-2]):
            yar.append(float(speedArr[len(speedArr)-1]))
            xar.append(i)
            line.set_data(xar, yar)
            ax1.set_xlim(0, i+1)
            ax1.set_ylim(400, 1600)


    plotcanvas = FigureCanvasTkAgg(fig, root)
    plotcanvas.get_tk_widget().grid(column=1, row=1)
    ani = animation.FuncAnimation(fig, animate, interval=15000, blit=False)
    root.mainloop()

def plot4():
    root = Tk()
    root.geometry('1500x500')
    root.title('Live Temperature Plot')
    root.config(background='white')

    xar = []
    yar = []

    style.use('ggplot')
    fig = plt.figure(figsize=(14, 4.5), dpi=100)
    ax1 = fig.add_subplot(1, 1, 1)
    line, = ax1.plot(xar, yar, 'b', marker='o', label="Celsius Plot")
    ax1.set_xlabel("Number of reading")
    ax1.set_ylabel("Temperature in Celsius")
    legend = ax1.legend(loc='upper right')
    def animate(i):
        if float(tempArr[len(tempArr)-1])!=float(tempArr[len(tempArr)-2]):
            yar.append(float(tempArr[len(tempArr)-1]))
            xar.append(i)
            line.set_data(xar, yar)
            ax1.set_xlim(0, i+1)
            ax1.set_ylim(297-273, 309-273)


    plotcanvas = FigureCanvasTkAgg(fig, root)
    plotcanvas.get_tk_widget().grid(column=1, row=1)
    ani = animation.FuncAnimation(fig, animate, interval=15000, blit=False)
    root.mainloop()
    
def quit_button():
    global tkTop
    tkTop.destroy()
 
def temp_button():
    temp=inputTemp.get(1.0, tkinter.END+"-1c")
    output.insert(END, "Temperture is being maintained at "+temp+" Celsius.\n\n")
    temp = "H"+temp
    ser.write(bytes(temp, 'UTF-8'))

def pH_button():
    pH=inputpH.get(1.0, tkinter.END+"-1c")
    output.insert(END, "pH is being maintained at "+pH+".\n\n")
    pH = "P"+pH
    ser.write(bytes(pH, 'UTF-8'))

def stir_button():
    speed=inputSpeed.get(1.0, tkinter.END+"-1c")
    output.insert(END, "Speed is being maintained at "+speed+" RPM.\n\n")
    speed = "S"+speed
    ser.write(bytes(speed, 'UTF-8'))

#change the COM port below
ser = serial.Serial("/tmp/simavr-uart0", 9600)
print("Bioreactor Control System Starting...#1")
time.sleep(1)
print("Default Temperature has been set#2")
print("Default Stirring Speed has been set#3")
print("Default pH has been set#4")
print("Checking for System errors...#5")
time.sleep(3)
print("\nNO ERRORS WERE DETECTED#6\nBioreactor Control System GUI Loading...#7")
time.sleep(2)

tkTop = tkinter.Tk()
tkTop.geometry('1200x1000') #1100 x 1000 window
tkTop.title("Bioreactor Control System") #name in title bar

#label to display the status
varLabel = tkinter.IntVar()
tkLabel = tkinter.Label(textvariable=varLabel, )
varLabel.set("BIOREACTOR STATUS")
tkLabel.pack()
 
#button1 - Temp
button1 = tkinter.IntVar()
button1state = tkinter.Button(tkTop, text="Set Temp", command=temp_button, height = 10, width = 20, bd="2", bg="turquoise",)
button1state.place(x=0, y=0)

#inputTemp console
inputTemp = Text(tkTop, bd="2", bg="white", width="20", height="2", font="Arial",)
inputTemp.place(x=300, y=50)

#button2 - pH
button2 = tkinter.IntVar()
button2state = tkinter.Button(tkTop, text="Set pH", command=pH_button, height = 10, width = 20, bd="2", bg="turquoise",)
button2state.place(x=0, y=250)

#inputpH console
inputpH = Text(tkTop, bd="2", bg="white", width="20", height="2", font="Arial",)
inputpH.place(x=300, y=300)

#button3 - stir
button3 = tkinter.IntVar()
button3state = tkinter.Button(tkTop, text="Set Stirring\nspeed", command=stir_button, height = 10, width = 20, bd="2", bg="turquoise",)
button3state.place(x=0, y=500)

#inputSpeed console
inputSpeed = Text(tkTop, bd="2", bg="white", width="20", height="2", font="Arial",)
inputSpeed.place(x=300, y=550)

#Quit button
tkButtonQuit = tkinter.Button(tkTop, text="Quit", command=quit_button, height = 10, width = 20, bd="2", bg="turquoise",)
tkButtonQuit.place(x=0, y=750)

#Output console
output = scrolledtext.ScrolledText(tkTop, bd="2", bg="white", width="50", height="50", font="Arial",)
output.place(x=600, y=30)
output.focus()

tempArr = []
phArr = []
speedArr = []

t1 = threading.Thread(target = displayInfo)
t1.daemon = True
t1.start()

tkinter.mainloop()
