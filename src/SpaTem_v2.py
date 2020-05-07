import numpy as np;
import pandas as pd

INIT_MAPS ={}


def get_default_modelparams():
    modelParameter = {}
    modelParameter["pi"] = 0.02
    modelParameter["tE"] = 3
    modelParameter["tI"] = 6
    modelParameter["cw"] = 10
    modelParameter["ch"] = 5

    modelParameter["eBC"] = 2/3  
    modelParameter["eLD"] = 1/3
    modelParameter["eDB"] = 1/3  
    modelParameter["eRZ"] = 1/3
    modelParameter["eOZ"] = 1/2
    modelParameter["eHS"] = 1/4

    modelParameter["aR"] = 0.1

    ## number of positive case thresholds
    modelParameter["dhsThreshold"] = 1 
    modelParameter["dzOZThreshold"] = 1
    modelParameter["dzRZThreshold"] = 10

    modelParameter["dhsOffsetDays"] = 7
    modelParameter["dzOZOffsetDays"] = 21
    modelParameter["dzRZOffsetDays"] = 7
    
    return modelParameter


def preload(loadnow= False, district = "all"):
    
    if "popDataDF" not in INIT_MAPS or "cSparseMatrix" not in INIT_MAPS:
        loadnow = True
        
    if loadnow:
        INIT_MAPS["popDataDF"] = pd.read_csv("../data/" + district + "_population_data.csv")
        INIT_MAPS["cSparseMatrix"] = pd.read_csv("../output/" + district + "_cmatrix_results.csv")
    
    return INIT_MAPS["popDataDF"], INIT_MAPS["cSparseMatrix"]



# Sort distance data by name for easy matrix transformation
def initialise(initDataDF, popDataDF, cSparseMatrix, modelParameter):

    r = len(initDataDF.index)
    C_TPart_Matrix = cSparseMatrix['Cij'].to_numpy().reshape(r,r)
   
    initDataDF.sort_values(by=['name'], inplace=True)
    initDataDF.reset_index(drop=True, inplace=True)

    popDataDF.sort_values(by=['name'], inplace=True)
    popDataDF.reset_index(drop=True, inplace=True)


    initDataDF['N'] = popDataDF['N']
    initDataDF['type'] = popDataDF['type']
    initDataDF['district'] = initDataDF['name'].str.split("__",n = 2, expand = True)[1] 

    districts = initDataDF['district'].unique()

    ## Workplace matrix
    Wn = modelParameter["cw"]*C_TPart_Matrix
    
    return popDataDF, C_TPart_Matrix, districts, Wn, r


def isMitigationEnabled(day, strategyName, userParameterData):
    if strategyName in userParameterData:
        for strategy in userParameterData[strategyName]:
            if day >= strategy['startDay'] and day <= strategy['endDay']:
                return True
    return False


def get_mitigation_bases(r,modelParameter):

    #Normal Day
    Mn = np.ones((r,r))
    #Break the chain
    Mbc = Mn*modelParameter["eBC"]
    #complete lockdown
    Mld = Mn*modelParameter["eLD"]

    return Mn, Mbc, Mld


def get_distric_border_closure_mitigation(cSparseMatrix, r, modelParameter):
    cSparseMatrix['iNameDistrict'] = cSparseMatrix['iName'].str.split("__",n = 2, expand = True)[1] 
    cSparseMatrix['jNameDistrict'] = cSparseMatrix['jName'].str.split("__", n = 2, expand = True)[1] 

    cSparseMatrix.loc[cSparseMatrix['iNameDistrict']==cSparseMatrix['jNameDistrict'],'interDistrictFlag'] = 0
    cSparseMatrix.loc[cSparseMatrix['iNameDistrict']!=cSparseMatrix['jNameDistrict'],'interDistrictFlag'] = 1

    Mdb = cSparseMatrix['interDistrictFlag'].to_numpy().reshape(r,r)*modelParameter["eDB"]
    Mdb[Mdb==0] = 1
    return Mdb


def fillRegion(M, i, e):
    M[:,i] = e
    M[i,:] = e
    return M


def getHotSpotMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter):
    M = np.ones((r,r))
    if "hotSpots" not in userParameterData:
        return M
    for hotSpot in userParameterData['hotSpots']:
        if day >= hotSpot['startDay'] and day <= hotSpot['endDay']:
            region = hotSpot['name']
            regionIndex = initDataDF.index[initDataDF['name'] == region][0]
            M = fillRegion(M, regionIndex, modelParameter["eHS"])
    return M


def getRedZoneMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter):
    M = np.ones((r,r))
    if 'redZones' not in userParameterData:
        return M
    for redzones in userParameterData['redZones']:
        if day >= redzones['startDay'] and day <= redzones['endDay']:
            district = redzones['district']
            regionsInDistrictList = initDataDF.index[initDataDF['district'] == district]
            for regionsInDistrictIndex in regionsInDistrictList:
                fillRegion(M, regionsInDistrictIndex, modelParameter["eRZ"])
                
            
    return M



def getOrangeZoneMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter):
    M = np.ones((r,r))
    if 'orangeZones' not in userParameterData:
        return M
    for orangezones in userParameterData['orangeZones']:
        if day >= orangezones['startDay'] and day <= orangezones['endDay']:
            district = orangezones['district']
            regionsInDistrictList = initDataDF.index[initDataDF['district'] == district]
            for regionsInDistrictIndex in regionsInDistrictList:
                fillRegion(M, regionsInDistrictIndex, modelParameter["eOZ"])

    return M



def updateDynamicHotSpots(day, I, dynamicHotSpots, modelParameter):
    regionIndices = np.where(I*modelParameter["aR"] > modelParameter["dhsThreshold"])[0]
    newDynamicHotSpots = []
    for regionIndex in regionIndices:
        regionIndexUpdated = False;
        for dynamicHotSpot in dynamicHotSpots:
            if regionIndex == dynamicHotSpot["regionIndex"] and dynamicHotSpot["startDay"] <= day < dynamicHotSpot["endDay"]:
                dynamicHotSpot["endDay"] = max(dynamicHotSpot["endDay"], day+modelParameter["dhsOffsetDays"])
                regionIndexUpdated = True            
        
        if not regionIndexUpdated:
            newDynamicHotSpots.append({"regionIndex" : regionIndex, "startDay": day, "endDay":  day+modelParameter["dhsOffsetDays"]})    
    
    return dynamicHotSpots + newDynamicHotSpots

    


def getDynamicHotSpotMitigationMatrix(day, r, dynamicHotSpots, modelParameter):
    M = np.ones((r,r))
    for dynamicHotSpot in dynamicHotSpots:
        if day >= dynamicHotSpot['startDay'] and day <= dynamicHotSpot['endDay']:
            M = fillRegion(M, dynamicHotSpot['regionIndex'], modelParameter["eHS"])
    return M



def updateDynamicZones(day, I, R, districts, dynamicZones, initDataDF, modelParameter):
    if "dynamicOrangeZones" not in dynamicZones:
        dynamicZones["dynamicOrangeZones"] = []
    if "dynamicRedZones" not in dynamicZones:
        dynamicZones["dynamicRedZones"] = []
     

    dynamicOrangeZones = dynamicZones["dynamicOrangeZones"];
    dynamicRedZones = dynamicZones["dynamicRedZones"];
    
    newDynamicOrangeZones = []
    newDynamicRedZones = []
    
    refDay = day-1-modelParameter["dzOZOffsetDays"]
    
    for district in districts:
        districtISumCur = I[day-1][initDataDF.index[initDataDF["district"] == district]].sum()
        districtISumRef = I[refDay][initDataDF.index[initDataDF["district"] == district]].sum()
        districtRSumCur = R[day-1][initDataDF.index[initDataDF["district"] == district]].sum()
        districtRSumRef = R[refDay][initDataDF.index[initDataDF["district"] == district]].sum()
        
        districtNewIfromRef = (districtISumCur - districtISumRef) + (districtRSumCur - districtRSumRef)


        ## Red zone

        if districtISumCur*modelParameter["aR"] > modelParameter["dzRZThreshold"]:
            print(district, ' in Red Zone with ', districtISumCur, ' infected.')
            dynamicRedZoneUpdated = False;
            for dynamicRedZone in dynamicRedZones:
                if district == dynamicRedZone["district"]:
                    dynamicRedZone["endDay"] =  max(dynamicRedZone["endDay"], day+modelParameter["dzRZOffsetDays"])
                    dynamicRedZoneUpdated = True
            
            if not dynamicRedZoneUpdated:
                newDynamicRedZones.append({"district": district, "startDay": day, "endDay": day + modelParameter["dzRZOffsetDays"]});
                
        ## Orange Zone
        if modelParameter["dzOZThreshold"] <= districtISumCur*modelParameter["aR"] < modelParameter["dzRZThreshold"]:
            print(district, ' in Orange Zone with ', districtISumCur, ' infected.')
            dynamicOrangeZoneUpdated = False;
            for dynamicOrangeZone in dynamicOrangeZones:
                if district == dynamicOrangeZone["district"]:
                    dynamicOrangeZone["endDay"] =  max(dynamicOrangeZone["endDay"], day+modelParameter["dzOZOffsetDays"])
                    dynamicOrangeZoneUpdated = True
            
            if not dynamicOrangeZoneUpdated:
                newDynamicOrangeZones.append({"district": district, "startDay": day, "endDay": day + modelParameter["dzOZOffsetDays"]});
        
        ## Green Zone (Clear orange and red)
        if districtNewIfromRef < 1 and refDay >= 0:
            ## Clear orange and red
            for dynamicZone in dynamicOrangeZones + dynamicRedZones:
                if district == dynamicZone["district"]:
                    dynamicZone["endDay"] = day-1 
                    print(district, ' in Green Zone with', districtNewIfromRef, ' infected from ', refDay)        

    dynamicZones["dynamicRedZones"]     = dynamicZones["dynamicRedZones"]     +   newDynamicRedZones
    dynamicZones["dynamicOrangeZones"]  = dynamicZones["dynamicOrangeZones"]  +  newDynamicRedZones
    
    return dynamicZones


def getDynamicOrangeZoneMitigationMatrix(day,r, initDataDF, dynamicOrangeZones, modelParameter):
    M = np.ones((r,r))
    for dynamicOrangeZone in dynamicOrangeZones:
        if day >= dynamicOrangeZone['startDay'] and day <= dynamicOrangeZone['endDay']:
            district = dynamicOrangeZone['district']
            regionsInDistrictList = initDataDF.index[initDataDF['district'] == district]
            for regionsInDistrictIndex in regionsInDistrictList:
                fillRegion(M, regionsInDistrictIndex, modelParameter["eOZ"])
                
            
    return M



def getDynamicRedZoneMitigationMatrix(day, r, initDataDF,  dynamicRedZones, modelParameter):
    M = np.ones((r,r))
    for dynamicRedZone in dynamicRedZones:
        if day >= dynamicRedZone['startDay'] and day <= dynamicRedZone['endDay']:
            district = dynamicRedZone['district']
            regionsInDistrictList = initDataDF.index[initDataDF['district'] == district]
            for regionsInDistrictIndex in regionsInDistrictList:
                fillRegion(M, regionsInDistrictIndex, modelParameter["eRZ"])
                
            
    return M


def getMitigationMatrix(day, dynamicHotSpots, dynamicZones, userParameterData, r, initDataDF, modelParameter,Ms):
    ## Effective mitigation matrix
    Mn = Ms["Mn"]
    Mld = Ms["Mld"]
    Mdb = Ms["Mdb"]
    Mbc = Ms["Mbc"]
    Meffective = Mn
    
    if isMitigationEnabled(day,"completeLockDowns", userParameterData):
        Meffective = np.minimum(Meffective, Mld)
    
    if isMitigationEnabled(day,"districtLockDowns", userParameterData):
        Meffective = np.minimum(Meffective, Mdb)
    
    if isMitigationEnabled(day,"hotSpots", userParameterData):
        Mhs = getHotSpotMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter)
        Meffective = np.minimum(Meffective, Mhs)
    
    if isMitigationEnabled(day,"redZones", userParameterData):
        Mrz = getRedZoneMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter)
        Meffective = np.minimum(Meffective, Mrz)
    
    if isMitigationEnabled(day,"orangeZones", userParameterData):
        Moz = getOrangeZoneMitigationMatrix(day, r, userParameterData, initDataDF, modelParameter)
        Meffective = np.minimum(Meffective, Moz)
    
    if isMitigationEnabled(day,"dynamicHotSpots", userParameterData):
        Mdhs = getDynamicHotSpotMitigationMatrix(day, r, dynamicHotSpots, modelParameter)
        Meffective = np.minimum(Meffective, Mdhs)
    
    if isMitigationEnabled(day,"dynamicZones", userParameterData):
        if 'dynamicOrangeZones' in dynamicZones:
            MdzOZ = getDynamicOrangeZoneMitigationMatrix(day, r, initDataDF, dynamicZones['dynamicOrangeZones'], modelParameter)
            Meffective = np.minimum(Meffective, MdzOZ)
        if 'dynamicRedZones' in dynamicZones:
            MdzRZ = getDynamicRedZoneMitigationMatrix(day, r, initDataDf, dynamicZones['dynamicRedZones'], modelParameter)
            Meffective = np.minimum(Meffective, MdzRZ)

    if isMitigationEnabled(day,"breakTheChains", userParameterData):
        Meffective = np.multiply(Meffective, Mbc)
          
    return Meffective




def computeContactMatrix(day, dynamicHotSpots, dynamicZones, userParameterData, r, initDataDF, modelParameter, Wn, Ms):
    Meffective = getMitigationMatrix(day, dynamicHotSpots, dynamicZones, userParameterData, r, initDataDF, modelParameter, Ms)
    Cmitigated = np.multiply(Meffective,Wn)    
    np.fill_diagonal(Cmitigated, Cmitigated.diagonal() + modelParameter["ch"])
    return Cmitigated
    



def runloop_data_initialisation(initDataDF, r, NO_OF_DAYS):
    S = np.zeros((NO_OF_DAYS,r))
    E = np.zeros((NO_OF_DAYS,r))
    I = np.zeros((NO_OF_DAYS,r))
    R = np.zeros((NO_OF_DAYS,r))

    E[0] = initDataDF['E']
    I[0] = initDataDF['I']
    R[0] = initDataDF['R']
    S[0] = initDataDF['N'] - E[0] - I[0] - R[0]
    
    dynamicHotSpots = []
    dynamicZones = {}
    
    return S,E,I,R, dynamicHotSpots, dynamicZones


def timeloop(initDataDF, userParameterData, modelParameter, r, popDataDF,NO_OF_DAYS, Wn, districts, Ms ):

    S,E,I,R, dynamicHotSpots, dynamicZones = runloop_data_initialisation(initDataDF,r, NO_OF_DAYS)

    for day in range(1,NO_OF_DAYS):
        if isMitigationEnabled(day,"dynamicHotSpots", userParameterData):
            dynamicHotSpots = updateDynamicHotSpots(day, I[day-1], dynamicHotSpots, modelParameter);
    
        if isMitigationEnabled(day,"dynamicZones", userParameterData):
            dynamicZones = updateDynamicZones(day, I, R, districts, dynamicZones, initDataDF, modelParameter)
            
        C = computeContactMatrix(day, dynamicHotSpots, dynamicZones, userParameterData, r, initDataDF, modelParameter, Wn, Ms)
    
        IbyN = I[day-1] / popDataDF['N']
        leaveS = modelParameter["pi"] * S[day-1] * np.matmul(C, IbyN)
        leaveE = E[day-1]/modelParameter["tE"]
        leaveI = I[day-1]/modelParameter["tI"]
    
        S[day] = S[day-1] - leaveS
        E[day] = E[day-1] + leaveS - leaveE
        I[day] = I[day-1] + leaveE - leaveI
        R[day] = R[day-1] + leaveI
        
    return dynamicHotSpots, dynamicZones, I


def simulate(seed={}, mitigations={}, modelparams={}, number_of_days = 60, case_multiplier=1):
    
    userParameterNone = { "breakTheChains" : [], "completeLockDowns" :  [], "districtLockDowns" :  [], "hotSpots": [], "redZones": [], "orangeZones": [] }

    
    if len(mitigations) == 0:
        mitigations = userParameterNone
        
    if len(modelparams) == 0:
        modelparams = get_default_modelparams()
        
    
    popDataDF, cSparseMatrix = preload()
    
    
    #Initialisations
    initDataDF = pd.DataFrame(columns=['name', 'district','N','S','E','I','R'])
    initDataDF['name'] = popDataDF['name']
    popDataDF, C_TPart_Matrix, districts, Wn,r = initialise(initDataDF, popDataDF, cSparseMatrix, modelparams)
    
    initDataDF['S'] = initDataDF['N']  
    initDataDF['E'] = 0  
    initDataDF['I'] = 0  
    initDataDF['R'] = 0  
    
    for uname in seed.keys():
        vals = seed[uname]
        initDataDF[initDataDF["name"] == uname] = vals[0]


    Mn, Mbc, Mld = get_mitigation_bases(r,modelparams)
    Mdb = get_distric_border_closure_mitigation(cSparseMatrix, r, modelparams)
    Ms = {"Mn":Mn, "Mld":Mld, "Mbc": Mbc, "Mdb": Mdb}

    dynamicHotSpots, dynamicZones, I = timeloop(initDataDF, mitigations, modelparams, r, popDataDF, number_of_days, Wn, districts, Ms)


    resultsIDF = pd.DataFrame(I, columns=popDataDF['name'])
    result ={}
    for name in resultsIDF.columns:
        result[name] = resultsIDF[name].round().tolist()
    return result


if __name__ == "__main__":
    seed ={"Kavilumpara__Kozhikode" : [200,0]}
    myresult = simulate(seed)