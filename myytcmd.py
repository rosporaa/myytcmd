# -*- coding: utf-8 -*-
import subprocess as sb
import json, os, sys
import platform

def run(exeFile, dpath, cfgFile, fenc):
  try:
    cfgF = {}
    if os.path.exists(cfgFile):
      f = open(cfgFile, "r")
      cfgF = json.load(f)
      f.close()

      if "ytdlp_path" in cfgF  and  cfgF['ytdlp_path']:
        ypath = cfgF['ytdlp_path']
        if os.path.exists(ypath):
          exeFile = ypath
  except:
    pass

  if not os.path.exists(exeFile):
    print(f"* Chyba: Nenašiel som potrebný súbor '{exeFile}'")
    sys.exit(1)

  # update yt-dlp
  print (f"* Aktualizujem yt-dlp ({exeFile})...")
  try:
    with sb.Popen([exeFile, '-U'], stdout=sb.PIPE) as u1:
      for line in u1.stdout:
        pass #print (line)

    if u1.returncode != 0:
      print ("* Upozornenie: Chyba pri aktualizácii, skúsim použiť starú verziu ...")
      #raise sb.CalledProcessError(u1.returncode, u1.args)  
  except FileNotFoundError:
    print(f"* Chyba: Nenašiel som potrebný súbor '{exeFile}'")
    sys.exit(1)

  # load, test config
  try:
    cfgF = {}
    if os.path.exists(cfgFile):
      f = open(cfgFile, "r")
      cfgF = json.load(f)
      f.close()
      
      if "download_path" in cfgF  and  cfgF['download_path']  and  len(cfgF["download_path"]) > 0:
        j = 1
        volba = 0
        for i in cfgF["download_path"]:
          print (f'{j}. {i["descr"]:20s}\t{i["path"]}')
          j += 1

        while not volba:
          try:
            volba = int(input ("* ----------------------\n* Kam uložiť? (zadajte číslo): "))
          except:
            volba = 0

          if volba > j-1  or  volba < 1:
            volba = 0

        dpath = cfgF["download_path"][volba-1]["path"]
        if not os.path.isdir(dpath):
          print (f"* Nenašiel som {dpath}!")
          dpath = "."    
  except:
    pass

  if dpath == ".":
    print (f"* Všetky súbory ukladám do aktuálneho adresára.")
  else:
    print (f"* Všetky súbory ukladám do: {dpath}")

  # download files
  while True:
    adresa = ""
    execList = [exeFile, f'-P {dpath}']

    try:
      while not adresa:
        adresa = str(input ("* ----------------------\n* Zadajte adresu (ak skončiť, zadajte n): "))

      if adresa == 'n':
        break

      asplit = adresa.strip().split(" ")
      execList.extend(asplit)
    
      print ("* Sťahujem:")

      with sb.Popen(execList, stdout=sb.PIPE, bufsize=1, text=True, encoding=fenc, errors='backslashreplace') as p1:
        for line in p1.stdout:
          if line.find("[download]") != -1:
            print(line.replace("\n", "") + '\r', flush=True, end="")
          else:
            print(line, flush=True, end="")

      if p1.returncode > 1:
        print ("* Chyba: Nastala chyba pri spustení procesu yt-dlp ... ")
        raise sb.CalledProcessError(p1.returncode, p1.args)

    except KeyboardInterrupt:
      sys.exit(3)      
    except Exception as e:
      print (f"* Chyba: Výnimka {e}")
      sys.exit(4)


if __name__ == "__main__":
  osPS = os.path.sep

  dpath   = "."
  cfgFile = f".{osPS}myytcmd.json"
    
  if platform.system().lower() == "windows":
    # cygwin also
    fenc = 'cp1250'
    exeFile = f".{osPS}yt-dlp.exe"
  else:
    fenc = 'utf-8'
    exeFile = f".{osPS}yt-dlp"

  run(exeFile, dpath, cfgFile, fenc)
