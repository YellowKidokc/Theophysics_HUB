@echo off
setlocal

set ROOT=D:\GitHub\stratum\06_engines

mklink /D "%ROOT%\chi-evaluator" "\\192.168.2.50\brain\06_ENGINES\chi-evaluator"
mklink /D "%ROOT%\P01_implicit" "\\192.168.2.50\brain\06_ENGINES\P01_implicit"
mklink /D "%ROOT%\P02_recbole" "\\192.168.2.50\brain\06_ENGINES\P02_recbole"
mklink /D "%ROOT%\P03_lightfm" "\\192.168.2.50\brain\06_ENGINES\P03_lightfm"
mklink /D "%ROOT%\P05_ppk" "\\192.168.2.50\brain\06_ENGINES\P05_ppk"
mklink /D "%ROOT%\P06_river" "\\192.168.2.50\brain\06_ENGINES\P06_river"
mklink /D "%ROOT%\P07_markovify" "\\192.168.2.50\brain\06_ENGINES\P07_markovify"

endlocal
