import numpy as np
import pandas as pd

##---------Global Paramters ---------------##
modelParameter = {}
modelParameter["pi"] = 0.02
modelParameter["tE"] = 5
modelParameter["tI"] = 5
modelParameter["tH"] = 9
modelParameter["cw"] = 15
modelParameter["ch"] = 5

INIT_MAPS ={} ## This dict will be populated in preload function


## Differential equation
def deriv(y,contactRatio, modelParameter):
    Si, Ei, Ii, Hi, Ri = y
    dSdt = -modelParameter["pi"] * Si * contactRatio
    dEdt = (modelParameter["pi"] * Si * contactRatio) - (Ei/modelParameter["tE"])
    dIdt = (Ei/modelParameter["tE"]) -  (Ii/modelParameter["tI"])
    dHdt = (Ii/modelParameter["tI"]) - (Hi/modelParameter["tH"])
    dRdt = (Hi/modelParameter["tH"])
    return dSdt, dEdt, dIdt, dHdt, dRdt


## Find the contact ratio
def findSpatialContactRatioV2(Ci, I, N, cwi):
    c = cwi*Ci*I/N
    return c.sum()


## Find the contact ratio
def findSpatialContactRatio(name, NDict, yDict, cSparseMatrix, modelParameter):
    # TODO conver this to a matrix operation
    contactRatio = 0;
    Ci = cSparseMatrix[cSparseMatrix['iName']==name]
    cw = modelParameter["cw"]
    ch = modelParameter["ch"]
    
    for index, Cij in Ci.iterrows():
        jName = Cij['jName']
        cij = cw*Cij['Cij']

        if(jName == name):
            cij = (cw+ch)*Cij['Cij']
            
        Ij = yDict[jName][2]
        Nj = NDict[jName]
        contactRatio = contactRatio +  (cij*Ij/Nj)
    return contactRatio;
        


## derive next count for SEIHR compartments
def derivNext(y, rates) :
    S,E,I,H, R = y
    dSdt, dEdt, dIdt, dHdt, dRdt = rates
    S1 = S + dSdt
    E1 = E + dEdt
    I1 = I + dIdt
    H1 = H + dHdt
    R1 = R + dRdt
    if S1 <= 0:
        S1 = 0
    if E1 <= 0:
        E1 = 0
    if I1 <=0:
        I1 = 0
    if H1 <= 0:
        H1 = 0
    if R1 <= 0:
        R1 = 0
        
    return S1, E1, I1, H1, R1


def preload(district):
    initDataDF = pd.read_csv("data/" + district + "_init_data.csv")
    cSparseMatrix = pd.read_csv("data/" + district + "_cmatrix_results.csv")

    INIT_MAPS[district] ={}
    INIT_MAPS[district]["initDataDF"] = initDataDF
    INIT_MAPS[district]["cSparseMatrix"] = cSparseMatrix



def simulate(no_of_days = 50, district="all", seed={}, mittigations=[]):
    #TODO : Discuss with experts
    if no_of_days > 185:
        return("Simulation is limitted to six months")


    initDataDF = INIT_MAPS[district]["initDataDF"]
    initDataDF['S'] = initDataDF['N'] #Initial S should be Total Population
    initDataDF['E'] = 0  # May be related to primary contacts. Experts?
    initDataDF['I'] = 0  # This would be updated by INput
    initDataDF['H'] = 0  # Ignoring this now, but we have data!
    initDataDF['R'] = 0  # Ignoring this now, but we have daga!


    for key in seed.keys():
        vals =seed[key]
        if (type(vals) != list) or (len(vals) !=2):
            return("Wrong Seed Data. It should be dict, {NAME:[10,12]}")
        initDataDF.loc[initDataDF["name"] == key, "I"] = vals[0]
        initDataDF.loc[initDataDF["name"] == key, "E"] = vals[0]
        #TODO: How is exposed mapped to E? Cross check mapping with experts

    cSparseMatrix = INIT_MAPS[district]["cSparseMatrix"]

    ## Number of regions
    r = len(initDataDF.index)

    ## cijMatrix
    cijMatrix = cSparseMatrix['Cij'].to_numpy().reshape(r,r)
    
    ## Sort distance data by name for easy matrix transformation
    initDataDF.sort_values(by=['name'], inplace=True)

    ## Create cMatrix
    cwMatrix = np.full((r,r),modelParameter["cw"], dtype=float)
    np.fill_diagonal(cwMatrix, modelParameter["cw"] + modelParameter["ch"])

    yPrevDict = {}
    yNextDict = {}
    data = []
    IPrevArr = []
    NArray = []

    for index, row in initDataDF.iterrows():
        yPrevDict[row['name']] = row['S'], row['E'], row['I'], row['H'], row['R'] 
        IPrevArr.append(row['I'])
        NArray.append(row['S'] + row['E'] + row['I'] + row['H'] + row['R'])
    
    IPrev = np.array(IPrevArr);
    N = np.array(NArray);
    
    
    for day in range(1, no_of_days):
        INextArr = [];
        for index, row in initDataDF.iterrows():
            name = row['name'];
            y = yPrevDict[name]; 
            
            contactRatio = findSpatialContactRatioV2(cijMatrix[index], IPrev, N, cwMatrix[index])
            rates = deriv(y, contactRatio, modelParameter)
            yNext = derivNext(y, rates) 
            
            yNextDict[name] = yNext
            data.append({'name': name, 'day': day, 'S': yNext[0], 'E': yNext[1], 'I': yNext[2], 'H': yNext[3], 'R': yNext[4]})
            INextArr.append(yNext[2])
        
        yPrevDict = yNextDict
        IPrev = np.array(INextArr)

    resultsDF = pd.DataFrame(data)

    resultsDF = resultsDF[["name","day","I"]].round(0)

    return resultsDF

#On Load Execute this function - HACK
for district in ["all"]:
    preload(district)

if __name__ == "__main__":
    seed ={"Vorkady__Kasaragod":[20,200]}
    resultsDF = simulate(district="all", seed=seed)
    print(resultsDF)