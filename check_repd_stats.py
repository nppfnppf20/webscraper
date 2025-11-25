from backend.database import db
from collections import Counter

results = db.get_repd_data()
solar = len([r for r in results if r.get('Technology Type') == 'Solar Photovoltaics'])
wind = len([r for r in results if r.get('Technology Type') == 'Wind Onshore'])
battery = len([r for r in results if r.get('Technology Type') == 'Battery'])

print(f'Total filtered records: {len(results)}')
print(f'Solar PV (>=3MW): {solar}')
print(f'Wind Onshore: {wind}')
print(f'Battery: {battery}')
print('\nStatus breakdown:')

statuses = Counter([r['Development Status'] for r in results])
for status, count in statuses.most_common():
    print(f'  {status}: {count}')
