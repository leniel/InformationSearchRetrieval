from scipy import spatial

dataSetI = [1, 13, 15, 17]
dataSetII = [2, 9, 11, 25]
result = 1 - spatial.distance.cosine(dataSetI, dataSetII)

print(result)

dataSetI = [1, 13, 15, 17]
dataSetII = [1, 13, 15, 17]
result = 1 - spatial.distance.cosine(dataSetI, dataSetII)

# Similarity = 1 because vectors are equal and so distance = 0
print(result)