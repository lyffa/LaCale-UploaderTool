# LaCale Uploader Tool

Outil Python permettant d’analyser automatiquement un fichier vidéo (film ou série)
et de générer une fiche prête pour l’upload sur La-Cale à partir de MediaInfo.

## Fonctionnalités

- Résolution (SD, 720p, 1080p, 4K, 8K)
- Codec vidéo (x264, x265, HEVC, AVC, AV1…)
- SDR / HDR / Dolby Vision
- Source (BluRay, WEB-DL, WEBRip, HDLight, 4KLight…)
- Pistes audio par langue (VFF, VO, codec, etc)
- Sous-titres (Forced, Full, SDH…)
- Taille réelle du fichier

## Prérequis

### MediaInfo
Télécharger MediaInfo et placer l’exécutable ici :
C:\mediainfo\mediainfo.exe

### Python
Python 3 doit être installé.  
Aucune dépendance externe n’est nécessaire.

## Utilisation

Dans un terminal :
python LaCale_UploadHelper.py
Une fenêtre s’ouvre pour choisir un fichier vidéo.  
La fiche La-Cale est affichée automatiquement.

## Exemple
Qualité : 1080p (Full HD)
Codec Vidéo : HEVC/H265/x265
Caractéristiques : 10 bits, SDR
Source : BluRay, HDLight
Pistes Audio :
French (DTS-HD MA) [VFF]
English (AC3)
Sous-titres :
FR (Forced)
ENG
