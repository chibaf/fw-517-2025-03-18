class readser:

  def read(self,ser):
    import serial
    line = ser.readline()
    try:
      data=line.strip().decode('utf-8')
      data=data.split(",")
    except UnicodeDecodeError:
      return [" ",0]
    return data