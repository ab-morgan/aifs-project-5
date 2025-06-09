import pandas as pd

df = pd.read_json("./data/USAJobs Data/sample.json")
results = pd.DataFrame(df.loc['SearchResultItems','SearchResult'])
sample_descriptor = results.iloc[2].loc['MatchedObjectDescriptor']

print(df)
print()
print(sample_descriptor.keys())
print()
print(sample_descriptor["UserArea"]["Details"]["MajorDuties"])