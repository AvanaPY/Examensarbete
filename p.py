import time
import random
from physio.scenario import Scenario
from physio.model import Model, ModelUpdateState

scenario = Scenario(body_mass=80, insulin_sensitivity=0.2)
model = Model(scenario=scenario)
model.step(ModelUpdateState(50, 1)); print()

for i in range(1000):
    state = None
    
    u = random.random()
    if u < 0.05:
        state = ModelUpdateState(0, 4)
    elif u < 0.08:
        state = ModelUpdateState(50, 0)
    else:
        state = ModelUpdateState(0, 0)
        
    print(f'{i:4d}: ', end='')
    for value in [state.carbs, state.insulin]:
        print(f'{value:12.4f} ', end='')
    print(' | ', end='')
    
    model.step(state)
    o = model.output_vector()
    
    for value in o:
        print(f'{value:12.4f} ', end='')
    print(' | ')
    time.sleep(0.05)