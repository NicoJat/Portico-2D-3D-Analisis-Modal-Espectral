import numpy as np



'''
Espesctro Respuesta de la NEC
'''
def Spec_NEC(n, z, fa, fd, fs, r, I, R, fip, fie, scale):
    To = 0.1*fs*(fd/fa)
    Tc = 0.55*fs*(fd/fa)
    Tl = 2.4*fd*scale

    j = 0
    Spec1 = []
    SpecI1 = []
    Tmp = []
    for T in np.arange(0,Tl,0.01):
        if T <= To:
            Tmp.append(T)
            Spec1.append(z*fa*(1 + ((n-1)*(T/To)))*I)
            SpecI1.append(n*z*fa*I/(R*fip*fie))
        elif T > To and T < Tc:
            Tmp.append(T)
            Spec1.append(n*z*fa*I)
            SpecI1.append(n*z*fa*I/(R*fip*fie))
        else:
            Tmp.append(T)
            Spec1.append(n*z*fa*((Tc/T)**r)*I)
            SpecI1.append(n*z*fa*((Tc/T)**r)*I/(R*fip*fie))
        
        j+=1

    Spec = np.column_stack((Tmp,Spec1))
    SpecI = np.column_stack((Tmp,SpecI1))

    return Spec, SpecI, Tmp, To, Tc, Tl


'''
Espesctro Respuesta de la ASCE 7-16
'''
def Spec_ASCE7(Tl, Fa, Fv, Ss, S1, limite, R, fip, fie):
    Sms = Fa*Ss
    Sm1 = Fv*S1
    Sds = (2/3)*Sms
    Sd1 = (2/3)*Sm1
    Ts = Sd1/Sds
    To = 0.2*(Sd1/Sds)

    '''
    1era_porción de la curva, 0 <= T < T0
    Ver en sección 11.4-6
    Sa = Sds*(0.4+(0.6*T/T0))

    2da_porción de la curva, T0 <= T <= Ts
    Sds

    3era_porción de la curva, Ts <= T <= Tl
    Sa = Sd1/T

    4ta_porción de la curva
    Sa = (Sd1*Tl)/(T**2)
    '''

    j = 0
    Spec_ASCE = []
    SpecI_ASCE = []
    Tmp = []
    for T in np.arange(0,limite,0.01):
        if T <= To:
            Tmp.append(T)
            Spec_ASCE.append(Sds*(0.4+(0.6*T/To)))
            SpecI_ASCE.append(Sds*(0.4+(0.6*T/To))/(R*fip*fie))
        elif T > To and T < Ts:
            Tmp.append(T)
            Spec_ASCE.append(Sds)
            SpecI_ASCE.append(Sds/(R*fip*fie))
        elif T > Ts and T < Tl:
            Tmp.append(T)
            Spec_ASCE.append(Sd1/T)
            SpecI_ASCE.append((Sd1/T)/(R*fip*fie))
        else:
            Tmp.append(T)        
            Spec_ASCE.append((Sd1*Tl)/(T**2))    
            SpecI_ASCE.append(((Sd1*Tl)/(T**2))/(R*fip*fie))    
        j+=1

    Spec_ASCE = np.column_stack((Tmp,Spec_ASCE))
    SpecI_ASCE = np.column_stack((Tmp,SpecI_ASCE))

    return Spec_ASCE, SpecI_ASCE, Tmp


