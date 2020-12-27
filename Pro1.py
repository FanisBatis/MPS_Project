import os, sys
import numpy as np
from scipy.sparse import csr_matrix
import tkinter
from tkinter.filedialog import askopenfile

def readfile():
    root = tkinter.Tk()
    root.withdraw()
    print("Choose mps file:")
    filename = askopenfile(mode='r') #Επιλογή αρχείου
    rows, eqin, data, rhs, lis = [], [] ,[] ,[], [1,2,0,3,4] #Αρχικοποίηση πινάκων που θα χρειαστούν
    sector = 0 #τα τμήματα του mps αρχείου
    minmax = -1 #min ή max
    content = filename.readlines()
    for line in content:
        words = line.split() #Διαχωρισμός του αρχείου mps σε strings
        
        #Καθορισμός ενοτήτων του αρχείου    
        if words[0] in ["ROWS", "COLUMNS", "RHS", "ENDATA"] and len(line)<=23:
            sector += 1
            continue
        elif words[0] not in ["ROWS", "COLUMNS", "RHS", "ENDATA"] and sector < 1:
            continue

        #Όνομα αρχείου και είδος προβλήματος
        thenameoffile = content[0].split()[1]
        if "MAX" in content[0]:
            minmax = 1

        #Οι περιορισμού του προβλήματος
        if sector == 1:
            rows.append(line[4:len(line)-1].strip())
            eqin.append(line[1])  
        
        #Συντελεστές τεχνολογικών περιορισμών
        elif sector == 2:
            data.append(words[0])
            end = 2
            if len (words) > 3: end = 5 #Όταν οι περιορισμοί στο αρχείο επεκτείνονται και σε δευτερη στήλη
            data.append(words[1])
            try: data.append(float(words[2]))
            except: data.append(words[2])
            for i in range(2, end):
                if i < end-1:
                    data.append(words[lis[i]])
                else:
                   try: data.append(float(words[lis[i]]))
                   except: data.append(words[lis[i]])
       
        # Δεξιό μέρος
        elif sector == 3:
            if len(words) == 2:
                words.append(words[1])
            for i in range(2, len(words), 2):
                rhs.append(float(words[i]))
                
    #Συντελεστές αντικειμενικής συνάρτησης
    obj = str(rows[eqin.index('N')])
    cost = []
    darray = []
    for i in range(1, len(data), 3):
        if obj == data[i]:
            darray.append(i)
            cost.append(data[i-1])
            cost.append(data[i+1])
    #Επεξεργασία των τεχνολογικών περιορισμών και εισαγωγή με μήτρα
    rows2 = list(rows)
    rows.remove(obj) #Αφαίρεση γραμμών της αντικειμενικής συνάρτησης
    for i in reversed(darray):
        del data[i-1:i+2]
    cols, x, y, d = [], [], [], []
    [cols.append(i) for i in data[0:len(data):3] if i not in cols]
    for i in range(0, len(data),3):
        x.append(cols.index(data[i]))
        y.append(rows.index(data[i+1]))
        d.append(data[i+2])
    col1 = np.array(x)
    row1 = np.array(y)
    dat1 = np.array(d)
    a = csr_matrix((dat1, (row1, col1)), shape = (len(rows), len(cols))).toarray()
      
    #Δημιουργία αρχείου .txt        
    with open(os.path.splitext(filename.name)[0] + ".txt", "w") as f:
        f.write(thenameoffile) 
        f.write("\n")
        f.write("\n")
        f.write("MinMax = " + str(minmax) + "\n")
        f.write("\n")
        f.write("Eqin:\n")
        eqin.remove('N')
        for i in range (len(eqin)): #Μετατροπή περιορισμών σε -1, 0, 1
            if eqin[i] =="L":
                eqin[i] = -1
            elif eqin[i] =="E":
                eqin[i] = 0
            elif eqin[i] =="G":
                eqin[i] = 1
            f.write("[" + str(eqin[i]) + "]" + "\n")    
        f.write("\n")
        f.write("B:\n")
        for i in range (len(rhs)): 
            f.write("[" + str(rhs[i]) + "]" + "\n") 
        f.write("\n")
        f.write("A:\n")
        f.write(str(a) + "\n")
        f.write("\n")
        f.write("C:\n")
        for i in range (1, len(cost), 2):
            f.write("[" + str(cost[i]) + "]" + "\n")
    print('\n')
    print("File created. Please open the file from path directory.")  
    print('\n')      
    
readfile()