# -*- coding: utf-8 -*-
import subprocess as sb
import json, os, sys
import platform

def run(exeFile, dpath, cfgFile, fenc):
  # update yt-dlp
  print ("* Aktualizujem yt-dlp ...")
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
    if os.path.exists(cfgFile):
      f = open(cfgFile, "r")
      cfgF = json.load(f)
      f.close()

      if "download_path" in cfgF  and  cfgF['download_path']:
        dpath = cfgF['download_path']
        if not os.path.isdir(dpath):
          dpath = "."
          print (f"* Upozornenie: Adresár '{dpath}' neexistuje. Súbory uložím do aktuálneho adresára.")
        else:
          print (f"* Informácia: Súbory uložím do adresára '{dpath}'")
      else:
        print (f"* Upozornenie: Nesprávna položka v konfigurácii. Súbory uložím do aktuálneho adresára.")        
    else:
      print (f"* Upozornenie: Súbor konfigurácie neexistuje. Súbory uložím do aktuálneho adresára.")
  except:
    print (f"* Upozornenie: Konfig výnimka. Súbory uložím do aktuálneho adresára.")

  # download files
  while True:
    adresa = ""

    try:
      while not adresa:
        adresa = str(input ("* ---------------\n* Zadajte adresu: "))
    
      print ("* Sťahujem:")

      with sb.Popen([exeFile, f'{adresa}', f'-P {dpath}'], stdout=sb.PIPE, bufsize=1, text=True, encoding=fenc, errors='backslashreplace') as p1:
        for line in p1.stdout:
          if line.find("[download]") != -1:
            print(line.replace("\n", "") + '\r', flush=True, end="")
          else:
            print(line, flush=True, end="")

      if p1.returncode > 1:
        print ("* Chyba: Nastala chyba pri spustení procesu yt-dlp ... ")
        raise sb.CalledProcessError(p1.returncode, p1.args)

      again = str(input ("\n* Ak chcete stiahnuť ďalší súbor, stlačte a: ")).lower()

      if again != 'a':
        break
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