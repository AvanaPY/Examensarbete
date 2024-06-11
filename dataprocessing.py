from typing import List, Dict
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy
from datetime import datetime, timedelta

data_path           = 'data/CTR3_Public_Dataset-Anderson'
data_tables_path    = os.path.join(data_path, 'Data Tables')
cgm_data_path       = os.path.join(data_tables_path, 'MonitorCGM.txt')
total_bolus_data_path = os.path.join(data_tables_path, 'MonitorTotalBolus.txt')
enrollment_data_path  = os.path.join(data_tables_path, 'Enrollment.txt')

cgm_df = pd.read_csv(cgm_data_path, delimiter='|')
cgm_df = cgm_df.drop(columns=['RecID', 'LocalDtTmAdjusted'])
cgm_df['LocalDtTm'] = pd.to_datetime(cgm_df['LocalDtTm']).dt.round("5min")
cgm_df = cgm_df.sort_values(by=['DeidentID', 'LocalDtTm'])

bolus_df = pd.read_csv(total_bolus_data_path, delimiter='|')
bolus_df['LocalDtTm'] = pd.to_datetime(bolus_df['LocalDeliveredDtTm']).dt.round("5min")
bolus_df = bolus_df.drop(columns=['LocalDeliveredDtTm', 'RecID'])
bolus_df = bolus_df.sort_values(by=['DeidentID', 'LocalDtTm'])

enrollment_df = pd.read_csv(enrollment_data_path, delimiter='|')


phase_2_patients = [2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 17, 20]
patient_id = phase_2_patients[2]

patient_info = enrollment_df[enrollment_df['DeidentID'] == patient_id]

df_patient = cgm_df[cgm_df['DeidentID'] == patient_id]
patient_bolus = bolus_df[bolus_df['DeidentID'] == patient_id]

count = len(df_patient.index)
earliest = df_patient['LocalDtTm'].min()
latest   = df_patient['LocalDtTm'].max()

start_date = earliest   + timedelta(days=0)
end_date   = latest + timedelta(days=0)

mask = (df_patient['LocalDtTm'] > start_date) & (df_patient['LocalDtTm'] < end_date)
df_patient = df_patient[mask]
patient_bolus = patient_bolus[(patient_bolus['LocalDtTm'] > start_date) & (patient_bolus['LocalDtTm'] < end_date)]

daterange = pd.date_range(start=earliest, end=latest, freq='5min')

df_patient = df_patient.set_index('LocalDtTm')
df_patient = df_patient[~df_patient.index.duplicated()]
patient_bolus = patient_bolus.set_index('LocalDtTm')
patient_bolus = patient_bolus[~patient_bolus.index.duplicated()]

df_patient = df_patient.reindex(daterange)
patient_bolus = patient_bolus.reindex(daterange).fillna(0)

df_patient['DeliveredTotalBolus'] = patient_bolus['DeliveredValue']
df_patient = df_patient[df_patient['CGM'].notna()]

x = df_patient.index
y = df_patient['CGM']

print(patient_info)
print(f'\nPatient CGM')
df_patient.info()
print(df_patient)

plt.subplot(211)
plt.plot(x, y)

y = df_patient['DeliveredTotalBolus']
plt.subplot(212)
plt.scatter(x, y, s=1, c='red')

plt.tight_layout()
plt.show()