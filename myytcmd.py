# -*- coding: utf-8 -*-
import subprocess as sb
import json, os, sys, stat
import platform
import requests


def downloadYtWin(exeFile, url):
  try:
    r = requests.get(url, stream=True)
    if r.ok:
      with open(exeFile, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024 * 8):
          if chunk:
            f.write(chunk)
            f.flush()
            os.fsync(f.fileno())
      f.close()
    else:
      print(f"* Chyba: sťahovanie skončilo s chybou:\n {r.status_code}\n {r.text}")
      return -1
  except Exception as e:
    print (f"* Chyba: Výnimka {e}")
    return -1

  return 0   


def chooseSaveDir(cfgFile):
  dpath = "."

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
          print (f'{j}. {i["descr"]:26s}\t{i["path"]}')
          j += 1
        print (f'{j}. Ukonči program')

        while not volba:
          try:
            volba = int(input ("* ------------------------------\n* Kam uložiť? (zadajte číslo): "))
          except:
            volba = 0

          if volba == j:
            sys.exit(6)
          if volba > j  or  volba < 1:
            volba = 0

        dpath = cfgF["download_path"][volba-1]["path"]
        if not os.path.isdir(dpath):
          print (f"* Upozornenie: Nenašiel som adresár {dpath}")
          dpath = "."  
  except SystemExit:
    sys.exit(6)  
  except:
    pass

  return dpath


def run(exeFile, dpath, cfgFile, fenc, ytDownloadURL, platforma):
  justDownloaded = False

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
    if len(ytDownloadURL):
      print(f"* Pokúsim sa ho stiahnúť, moment prosím...")    
      if downloadYtWin(exeFile, ytDownloadURL) == -1:
        sys.exit(1)
      else:
        if os.path.exists(exeFile):
          if platforma.find("linux")  or  platforma.find("cygwin"): 
            st = os.stat(exeFile)
            os.chmod(exeFile, st.st_mode | stat.S_IEXEC)
          justDownloaded = True
          print (f"* Súbor {exeFile} stiahnutý.")      

  if not justDownloaded:
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

  dpath = chooseSaveDir(cfgFile)

  if dpath == ".":
    print (f"* Súbory ukladám do aktuálneho adresára.")
  else:
    print (f"* Súbory ukladám do: {dpath}")

  # download files
  while True:
    adresa = ""
    execList = [exeFile, f'-P {dpath}']

    try:
      while not adresa:
        adresa = str(input ("* ------------------------------\n* Zadajte adresu (k - koniec, z - zmena adresára): "))

      if adresa == 'k':
        break

      if adresa == 'z':
        dpath = chooseSaveDir(cfgFile)

        if dpath == ".":
          print (f"* Súbory ukladám do aktuálneho adresára.")
        else:
          print (f"* Súbory ukladám do: {dpath}")  

        execList = [exeFile, f'-P {dpath}']
        continue

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


# MAIN
if __name__ == "__main__":
  cfgFileName   = "myytcmd.json"
  ytExecNameUnx = "yt-dlp"
  ytExecNameWin = "yt-dlp.exe"
  ytExecNameMac = "yt-dlp_macos"
  ytDownloadURLWin = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
  ytDownloadURLLin = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp'
  ytDownloadURLMac = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos'

  osPS = os.path.sep

  dpath   = "."
  cfgFile = f".{osPS}{cfgFileName}"
    
  pt = platform.system().lower() 
  if pt == "windows":
    fenc = 'cp1250'
    exeFile = f".{osPS}{ytExecNameWin}"
    ytDownloadURL = ytDownloadURLWin
  elif pt.find("linux") != -1:
    fenc = 'utf-8'
    exeFile = f".{osPS}{ytExecNameUnx}"
    ytDownloadURL = ytDownloadURLLin
  elif pt.find("cygwin") != -1:
    fenc = 'utf-8'    
    exeFile = f".{osPS}{ytExecNameWin}"
    ytDownloadURL = ytDownloadURLWin
  elif pt.find("darwin") != -1:
    fenc = 'utf-8'    
    exeFile = f".{osPS}{ytExecNameMac}"
    ytDownloadURL = ytDownloadURLMac
  else:
    fenc = 'utf-8'
    exeFile = f".{osPS}{ytExecNameUnx}"
    ytDownloadURL = ""
    print (f"* Upozornenie: Neznáma platforma. Skúsim použiť {exeFile}.")

  run(exeFile, dpath, cfgFile, fenc, ytDownloadURL, pt)
