# -*- coding: utf-8 -*-
import subprocess as sb
import json, os, sys
import platform

def run(exeFile, dpath, cfgFile):
  try:
    if os.path.exists(cfgFile):
      f = open(cfgFile, "r")
      cfgF = json.load(f)
      f.close()

      if "download_path" in cfgF  and  cfgF['download_path']:
        dpath = cfgF['download_path']
        print (f"* Uložím do adresára '{dpath}'")
    else:
      print (f"* Bez konfigurácie. Uložím do adresára '{dpath}'")
  except:
    print (f"* Cfg exeption. Uložím do adresára '{dpath}'")

  print ("* Aktualizujem...")
  try:
    with sb.Popen([exeFile, '-U'], stdout=sb.PIPE) as u1:
      for line in u1.stdout:
        pass #print (line)

    if u1.returncode != 0:
      print ("* Chyba pri aktualizázii, skúsim použiť starú verziu...")
      #raise sb.CalledProcessError(u1.returncode, u1.args)  
  except FileNotFoundError:
    print(f"* Chyba: Nenašiel som súbor '{exeFile}'")
    sys.exit(1)

  adresa = ""

  try:
    while not adresa:
      adresa = str(input ("* Zadaj adresu videa: "))
  except KeyboardInterrupt:
    sys.exit(2)

  print ("* Sťahujem:")

  try:
    with sb.Popen([exeFile, f'{adresa}', f'-P {dpath}'], stdout=sb.PIPE, bufsize=1, universal_newlines=True) as p1:
      for line in p1.stdout:
        if line.find("[download]") != -1:
          print(line.replace("\n", "") + '\r', flush=True, end="")
        else:
          print(line, flush=True, end="")

    if p1.returncode > 1:
      print ("* Nastala chyba pri spustení procesu yt-dlp.exe: ")
      raise sb.CalledProcessError(p1.returncode, p1.args)
  except KeyboardInterrupt:
    sys.exit(3)      
  except Exception as e:
    print (f"* Chyba: Výnimka {e}")


if __name__ == "__main__":
  try:
    osPS = os.path.sep

    dpath   = "."
    cfgFile = f".{osPS}myytcmd.json"
    
    if platform.system().lower() == "windows":
      exeFile = f".{osPS}yt-dlp.exe"
    else:
      exeFile = f".{osPS}yt-dlp"

    run(exeFile, dpath, cfgFile)
    input ("\n* Stlač ENTER...")
  except KeyboardInterrupt:
    sys.exit(4)
