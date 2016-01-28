import os
import csv
import errno
import shutil
import re
import getpass
from time import localtime, strftime

time = "000"
rev = "V0.1"
user = getpass.getuser()

def make_sure_path_exists(path):
		try:
			os.makedirs(path)
			#write_logg ("logg","make_sure_path_exists"," Lagde mappe %s","" % (path))
		except OSError as exception:
			 if exception.errno != errno.EEXIST:
				 raise
make_sure_path_exists ("admin")
make_sure_path_exists ("./admin/backup")

def get_time(t):
	time = strftime("%d %b %Y %H:%M:%S", localtime())
	return time

def write_logg(loggtype,start, mid, end):
	time = get_time("time")
	time_and_user = time+" "+user
	file = "./admin/"+loggtype+".txt"
	logg = open(file, "a")
	logg.write ("%s: %s %s %s \n" % (time_and_user, start, mid, end))
	logg.close()

write_logg ("logg","--  Script startet  --",rev,"")

#Alt 1
def MoveToRoot():
	NameToFile()
	Flyttet = 0
	write_logg ("logg","Flytter filer til rot","","")
	NameToFile()
	filesList = os.walk(".")
	for root, folder, file in filesList:
		for f in file:
			if os.path.join(root,"").startswith(".\\admin"):
				continue
			toMove = root + "/" + f
			print (toMove)
			try:
				os.rename(toMove, f)
				Flyttet = Flyttet + 1
			except Exception as e:
				print ("Kunne ikke flyte "+toMove)
	write_logg ("logg",Flyttet,"Flyttet til rot","")
	print (Flyttet)
	print ("Filer flyttet til rot")

def removeEmptyFolders(path):
	if not os.path.isdir(path):
		return

	# remove empty subfolders
	files = os.listdir(path)
	if len(files):
		for f in files:
			fullpath = os.path.join(path, f)
			if os.path.isdir(fullpath):
				removeEmptyFolders(fullpath)

	# if folder empty, delete it
	files = os.listdir(path)
	if len(files) == 0:
		print ("Removing empty folder:", path)
		os.rmdir(path)

def NameToFile ():
	AntallFiler = 0
	with open('./admin/filnavn.csv', 'w') as csvfile:
		ny = csv.writer(csvfile, delimiter=';', lineterminator='\n', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		ny.writerow (["NewPath", "NewName", "OldPath","OldName", "Filtype"])
		for root, dirs, files in os.walk('.'):
			for fil in files:
				fileName, fileExtension = os.path.splitext(fil)
				#test123 = (os.path.join(root,""))
				if os.path.join(root,"").startswith(".\\admin"):
					print ("gogogog")
					continue
				if fileName == "01FileManager":
					continue

				AntallFiler = AntallFiler + 1
				ny.writerow ([os.path.join(root,""), fileName, os.path.join(root,""), fileName, fileExtension])
	write_logg ("logg","NameToFile ",AntallFiler," Filer registrert")
	print ("\n")
	print (str(AntallFiler)+" filer registrert")



def FilePathBackup():
	time = strftime("%d%b%Y_%H%M%S", localtime())
	shutil.copy("./admin/filnavn.csv", "./admin/backup")
	os.rename ("./admin/backup/filnavn.csv", "./admin/backup/filnavn%s.csv" % (time))

def RenameFromFile():
	write_logg ("logg","RenameFromFile","","")
	with open('./admin/filnavn.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		# for row in reader[1:]:
		next(reader)
		for row in reader:
			for st in row:
				f = st.split (";")
				if len(f) == 5:
					a = f[2]+f[3]+f[4]
					b = f[0]+f[1]+f[4]
					if not a == b:
						try:
							make_sure_path_exists (f[0])
							os.rename (f[2]+f[3]+f[4], f[0]+f[1]+f[4])
							#write_logg ("logg_filflytt",a,"<byttet navn til>",b)
						except:
							#print (("Kunne ikke flytte fil %s %s %s") % (f[2],f[3],f[4]))
							print (("Kunne ikke flytte fil %s") % (f[1]))
							pass

def FindAndReplace():
	fra = input("\n\nHva skal ersteattes: ")
	til = input("Hva skal det erstattes med: ")

	pathiter = (os.path.join(root, filename)
		for root, _, filenames in os.walk(".")
		for filename in filenames
	)

	try:
		for path in pathiter:
			newname =  path.replace(fra, til)
			if newname != path:
				if not path.startswith(".\\admin"):
					os.rename(path,newname)
	except:
		print ("Fant ikke noe og erstatte")
	print ("RUN")



#Flytter pdf filer med formatet E6.B.500-411_REV_A.pdf (Ma besta av 7 deler delt med  -_.)
#Flyttes i mapper etter valgt inndeling
def move_file(f):
	filename_spit = re.split(r'[.|_|-]', f)
	filtype = filename_spit[-1] #Part "-1"
	riktig_filtype = "pdf"
	antall_filnavn_deler = len(filename_spit)
	file_ok = riktig_filtype == filtype and antall_filnavn_deler == 7

	if file_ok == True:
		part1 = filename_spit[0] # Tegnings type (E6)
		part2 = filename_spit[1] # Bygg (A)
		part4 = filename_spit[3] # System (411)
		part6 = filename_spit[5] # REV (Rev bokstaven)
		new_path = "%s\\%s\\%s" % (part1, part2, part4)
		new_name = "%s\\%s" % (new_path, f)
		make_sure_path_exists (new_path)
		try:
			os.rename (f, new_name)
			#write_logg (f, "flyttet til mappe", new_path)
		except WindowsError:
			pass
				#write_logg (f, "ligger alt i en mappe"," ")
	#else:
		#if filtype != riktig_filtype:


		#else:
			#if antall_filnavn_deler != 7:



#Flytter en fil lavere Rev til utgatt mappen.
#Siste tegn i filnavnet ma vere REV bokstav/nr.
#Hvis det er hoppet over en rev vil den gamle revs ikke bli flyttet
def move_old_revs(f):
	clean_name = ''.join(f.split())[:-4]
	cur_rev = clean_name[-1]
	old_rev = chr(ord(cur_rev)-1)
	new_name = clean_name [:-1]+old_rev+".pdf"
	filename_spit = re.split(r'[.|_|-]', new_name)

	part1 = filename_spit[0] # Tegnings type (E6)
	part2 = filename_spit[1] # Bygg (A)
	part4 = filename_spit[3] # System (411)
	part6 = filename_spit[5] # REV (Rev bokstaven)

	old_path = "%s\\%s\\%s" % (part1, part2, part4)
	old_name = "%s\\%s" % (old_path, new_name)

	new_path = "Utgatt\\%s\\%s\\%s" % (part1, part2, part4)
	new_name2 = "%s\\%s" % (new_path, new_name)


	try:
		if not os.path.isfile(old_name):
			raise OSError("File not found")
		make_sure_path_exists (new_path)
		try:
			os.rename (old_name, new_name2)
			#write_logg ("Rev utgatt", new_name, "flyttet til utgatt mappen")
		except:
			#write_logg(new_name, "er utgatt men finnes alt i utgatt mappen"," ")
			pass
	except:
		pass

def FileSorter():
	#Lager en liste med alle filer i root mappen
	files = [f for f in os.listdir('.') if os.path.isfile(f)]

	#Kjorer def move_file pa alle filer i rootmappen
	for f in files:
		move_file (f)


def SortByFileType():
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	for f in files:
		if os.path.isfile(f):
			FileType = os.path.splitext(f)[1][1:]
			print (f)
			if f == "01FileManager.py":
				continue
			if len(FileType) == 0:
				continue
			make_sure_path_exists (FileType)
			move_from = "./"+f
			move_to = "./"+FileType+"/"+f
			os.rename (move_from, move_to)


#Gar gjennom alle mapper med unntak av utgattmappen og kjorer move revs
def FilesInFolder():
	make_sure_path_exists ("Utgatt")
	mapper = []
	for x in os.listdir('.'):
		if os.path.isfile(x):
			pass
		else:
			mapper.append (x)
	mapper.remove ("Utgatt")

	filer = []
	for f in mapper:
		for root, dirs, files in os.walk(f, topdown=True):
			for name in files:
				filer.append(name)

	for f in filer:
		try:
			move_old_revs (f)
		except:
			pass


def main(valg):
	try:
		FilePathBackup()
	except:
		pass
	valg = 0
	print ("\n\n")
	print ("Alternativ 1 : Filnavn til fil")
	print ("Alternativ 2 : Endre filnavn fra fil")
	print ("Alternativ 3 : Flytt alle filer til Root")
	print ("")
	print ("Alternativ 4 : Slett alle tomme mapper")
	print ("Alternativ 5 : Finn og erstatt i filnavn")
	print ("Alternativ 6 : FileSorter")
	print ("Alternativ 7 : Sorter etter fil type")

	print ("")
	print ("")
	print ("Alternativ 9 : --  QUIT  -- \n")
	try:
		valg = int(input("Velg et alternativ: "))
		write_logg("logg", "Alternativ", valg, "valgt")
	except:
		valg = 0
		print ("\n INGEN GYLDIG ALTAERNATIV VALGT \n")
	if valg == 1:
		NameToFile()
	if valg == 2:
		RenameFromFile()
	if valg == 3:
		MoveToRoot()
	if valg == 4:
		print ("\nEr du sikker? Dette vil slette alle tomme mapper i denne mappen \n")
		sikker = "N"
		sikker = str.upper(input("Y/N: "))
		if sikker == "Y":
			removeEmptyFolders(".")
	if valg == 5:
		FindAndReplace()
	if valg == 6:
		FileSorter()
		FilesInFolder()
	if valg == 7:
		SortByFileType()
	return valg
valg = 0
while valg != 9:
	valg = main(valg)
write_logg ("logg","--  Script avsluttet uten feil  --","","")
