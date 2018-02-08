from PIL import Image, ImageDraw
import sys
from tqdm import tqdm


def foo(count):
	return [-2 + (4/(count-1)) *x for x in range(0, count) ]
	
def bar(count):
	delta = (2/(count-1))
	lists = []
	lists.append([-2 + delta * x for x in range(0, count)])
	for y in range(1, count):
		lists.append([ prev + delta for prev in lists[y-1]])
	return lists

	
def color_mapper(norm):
	"""normalized float to RGB tupple converter"""
	red = (2/3 - norm) * (3/2) if norm < 2/3 else 0
	green = abs(norm - .5) * 6 if 1/3 < norm < 2/3 else 0
	blue = (norm - (1/3)) * (3/2) if norm > 1/3 else 0
	return (int(255*red), int(255*green), int(255*blue))
	
	
	
def colorer(grid):
	max_ = max([max(row) for row in grid])
	min_ = min([min(row) for row in grid])
	
	print("{} - {}".format(max_, min_))

	image = Image.new('RGB', (len(grid), len(grid[0])))
	draw = ImageDraw.Draw(image)
	for row_index, row in tqdm(enumerate(grid)):
		for col_index, value in enumerate(row):
			# print((value - min_) / (max_ - min_))

			draw.point((row_index, col_index), (color_mapper((value - min_) / (max_ - min_))))
	image.save('image.png')
	
if __name__ == "__main__":		
    colorer(bar(100))
