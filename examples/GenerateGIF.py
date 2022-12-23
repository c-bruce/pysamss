import glob
import imageio

image_files = sorted(glob.glob('*.png'))

images = []
for image_file in image_files:
    images.append(imageio.imread(image_file))

imageio.mimsave('movie.gif', images, fps=50)
