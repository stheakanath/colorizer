# Kuriakose Sony Theakanath
# Colorizing the Prokudin-Gorskii photo collection

from PIL import Image
import time
import skimage.io as skio
import itertools
import sys

DEFAULT_ITERATIONS = 3

def move(im, dx, dy):
	changesx, changesy, total = 0, 0, 0
	width, height = im.size
	orig, after = im.load(), Image.new('L', im.size)
	afterpixels = after.load()
	for i, j in itertools.product(range(width), range(height)):
		x, y = (i + dx) % width, (j + dy) % height
		changesx += abs(x - i)
		changesy += abs(y - j)
		total += 1
		afterpixels[i, j] = orig[x, y]
	return after, changesx / total, changesy / total

# Main Code
imname = "a_orig.jpg"
print "Converting " + imname
if "tif" in imname:
	print "16 bit image detected. Converting image to 8 bit."
	im = Image.open(imname)
	im.mode = 'I'
	im = im.point(lambda i:i*(1./256)).convert('L')
	DEFAULT_ITERATIONS = 3
	print "Finished converting image to 8 bit, now applying algo."
else:
	DEFAULT_ITERATIONS = 3
	im = Image.open(imname)

# color1 - blue, color2 - green, color3 - red

# Splitting the images into thirds
for x in range(1, 4):
	globals()['color%s' % x] = im.crop((0, im.size[1] / 3 * (x - 1), im.size[0], im.size[1] / 3 * x))

# Pyramid algorithm for large TIFF images
colors, (width, height) = [[color1], [color2], [color3]], color3.size

while (width > 100):
	for x in range(3):
		colors[x].append(globals()['color%s' % (x + 1)].resize((width / 2, height / 2)))
	width, height = width / 2, height / 2

# Reversing to go from small to large
colors = [colors[2][::-1], colors[1][::-1], colors[0][::-1]]
bluealignx, greenalignx, bluealigny, greenaligny, totalgreen, totalblue = 0, 0, 0, 0, 0, 0

for i in range(len(colors[0])):
	border, diffgreen, diffblue, n = colors[2][i].size[0] / 3, [], [], DEFAULT_ITERATIONS
	start_time = time.time()
	for dx, dy in itertools.product(range(-n, n + 1), range(-n, n + 1)):
		blue_loaded, green_loaded, red_loaded, (width, height), green_sum, red_sum = colors[2][i].load(), colors[1][i].load(), colors[0][i].load(), colors[2][i].size, 0, 0
		for l, j in itertools.product(range(border, width - border), range(border, height - border)):
			x, y = (l + dx) % width, (j + dy) % height
			green_diff, red_diff = abs(blue_loaded[l,j] - green_loaded[x, y]), abs(blue_loaded[l,j] - red_loaded[x, y])
			green_sum, red_sum = green_sum + green_diff ** 2, red_sum + red_diff ** 2
		diffgreen.append(((dx, dy), green_sum))
		diffblue.append(((dx, dy), red_sum))
	print("--- Loop %s seconds ---" % (time.time() - start_time))
	# End image pyramid

	# Alignment procedure
	dxgreen, dygreen = min(diffgreen, key = lambda imagearr: imagearr[1])[0]
	dxblue, dyblue = min(diffblue, key = lambda imagearr: imagearr[1])[0]
	for j in range(i, len(colors[0])):
		colors[1][j], greenalignxtmp, greenalignytmp = move(colors[1][j], dxgreen, dygreen)
		greenalignx += greenalignxtmp
		greenaligny += greenalignytmp
		totalgreen += 1
		colors[0][j], bluealignxtmp, bluealignytmp = move(colors[0][j], dxblue, dyblue)
		bluealignx += bluealignxtmp
		bluealigny += bluealignytmp
		totalblue += 1
		dxgreen, dygreen, dxblue, dyblue = dxgreen * 2, dygreen * 2, dxblue * 2, dyblue * 2

r, rp, gp, bp = colors[0][-1].size, colors[0][-1].load(), colors[1][-1].load(), colors[2][-1].load()
colored = Image.new('RGBA', r)
pixels = colored.load()

for x, y in itertools.product(range(r[0]), range(r[1])):
	pixels[x,y] = (rp[x,y], gp[x,y], bp[x,y], 100)
print "Output is saved as output.jpg in same folder!"
skio.imsave("output.jpg", colored)