from pipe import izip, map, select

data = list(['a', 'b']
            | izip(['1', '2'])
            | select(lambda x, y: x+y))

print(data)
