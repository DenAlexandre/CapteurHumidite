# utils/fileUtility.py
    
def WriteFile(filename, txt):
	fichier = open(filename, "a")
	fichier.write(txt + "\n")
	fichier.close()

