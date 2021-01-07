import pandas as pd
from matplotlib import pyplot as plt

obs = pd.read_csv('observations.csv')
si = pd.read_csv('species_info.csv')

# Left Merge species_info.csv onto observations.csv to get the animal details of each observation instance.
obs = obs.set_index('scientific_name')

# Some species have duplicate records, differing only in common name. Drop these.
si = si.drop_duplicates(subset=['scientific_name'])
si = si.set_index('scientific_name')

df = obs.join(si, on='scientific_name', how='left')
df['conservation_status'] = df['conservation_status'].apply(lambda row: 'Least Concern' if pd.isna(row) else row)
# For brevity, change 'Vascular Plant' to 'V Plant', and 'Nonvascular Plant' to 'NV Plant'
df['category'] = df['category'].apply(lambda row: 'V Plant' if row == 'Vascular Plant' else row)
df['category'] = df['category'].apply(lambda row: 'NV Plant' if row == 'Nonvascular Plant' else row)

status_labels = df.conservation_status.unique()
species_types = ['V Plant', 'NV Plant', 'Mammal', 'Bird', 'Reptile', 'Amphibian', 'Fish']
species_colors = ['forestgreen', 'limegreen', 'brown', 'blue', 'orange', 'teal', 'aqua']

# Question: Are certain species categories (e.g. birds) more likely to be endangered?

# First, find proportions of each species category for all data.
species_freqs = df.category.value_counts(normalize=True)
species_freqs = species_freqs.multiply(100)
print('Species Proportions (%) for All Data')
print(species_freqs)

print('')

# Next, find proportions of each species category for each conservation level
fig = plt.figure(figsize=(14, 10))
for i, status in enumerate(status_labels):
    fig.add_subplot(2, 3, i+1)
    subframe = df[df['conservation_status'] == status]
    num_observations = len(subframe)
    species_freqs_status = subframe.category.value_counts(normalize=True).multiply(100)
    freq_dict = species_freqs_status.to_dict()

    print(f'Species Proportions (%) for status: {status}')
    print(species_freqs_status)
    print('')

    freq_lst = []
    for species in species_types:
        freq_lst.append(freq_dict.get(species, 0))
    plt.bar(species_types, freq_lst, color=species_colors)
    plt.title(f'{status}: {num_observations} Species Total')
    plt.xlabel('Species Category')
    plt.xticks(rotation=52)
    plt.ylabel(f'Porportion (%)')
    plt.axis([-1, 7, 0, 100])
plt.subplots_adjust(hspace=0.4, wspace=0.25)
fig.suptitle('Species Category Proportions for Each Conservation Status')
plt.show()

# Find the rate/proportion of each species being at least 'Species of Concern.'
df['concerned'] = df.conservation_status.apply(lambda row: 1 if row != 'Least Concern' else 0)
proportion = df.groupby('category').concerned.sum()
proportion = proportion.divide(df.groupby('category').concerned.count())
proportion = proportion.multiply(100).round(2)
print('Proportion of Each Species NOT Having "Least Concern" Status:')
for ind, prop in proportion.to_dict().items():
    print(f'{ind}: {prop} %')
