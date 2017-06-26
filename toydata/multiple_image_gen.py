from toydatabasic import*
from toydatabasic import _choose_rectangle
from toydatabasic import _choose_triangle
from toydatabasic import _choose_vertical
from toydatabasic import _choose_horizontal
from toydatabasic import _image
from classification_image_gen import generate_noise
from toydata_varconfig import test_image

img = test_image()
#labeling still needs to be fixed!!!!!!!!!

def _choose_random_pixel(array):
    row = np.random.randint(img.SHAPE_SIZE, array.shape[0]-img.SHAPE_SIZE)
    col = np.random.randint(img.SHAPE_SIZE, array.shape[1]-img.SHAPE_SIZE)
    return row, col

def _randomize_shape(chance):
    """function to return True depending on 1/chance input. Takes an integer
    you really shouldn't have to mess with this."""
    z = np.random.randint(0, chance)
    if z < 1:
        return True
    else: return False

def _make_2d_labels(locs, nshapes = 4, maxmult = 5):
    """This function takes in an array with labels from all the *individual* shapes in an image,
    and generates a 2D array with shape type and multiplicities."""
    label_array = np.zeros([maxmult, nshapes])
    for _ in range(nshapes):
        tester = [0,0,0,0]
        tester[_] = 1
        colval = 0
        for element in locs:
            if element == tester:
                colval += 1
        label_array[colval][_] = 1

    return label_array

def _add_multiple_shapes_to(array, vals, nums = img.MULTIPLICITIES, probs = 3, types = img.ALLOWED):
    """
    This function populates an array with random shapes.
    The inputs are as follows:
    1. an array of any dimension, to be populated with shapes
    2. a list to be populated with image labels
    3. a list of booleans corresponding to the shapes to be generated:
    [square, triangle, horizontal, vertical]
    4. a list of allowed maximum multiplicities for each shape:
    ex: [2, 2, 2, 2]
    5. an integer corresponding to the likelihood of generating a shape at a
    given location: for example, an input of 4 corresponds to a 1/4 chance
    that each allowed shape will actually exist"""
    locs = []
    if types[0]:
        for i in range(nums[0]):
            x, y = _choose_random_pixel(array)
            if _randomize_shape(probs):
                _choose_rectangle(x, y, array)
                if True:
                    locs.append([1,0,0,0])
    if types[1]:
        for i in range(nums[1]):
            x, y = _choose_random_pixel(array)
            if _randomize_shape(probs):
                _choose_triangle(x, y, array)
                if True:
                    locs.append([0,1,0,0])
    if types[2]:
        for i in range(nums[2]):
            x, y = _choose_random_pixel(array)
            if _randomize_shape(probs):
                 _choose_horizontal(x, y, array)
                 if True:
                    locs.append([0,0,1,0])
    if types[3]:
        for i in range(nums[3]):
            x, y = _choose_random_pixel(array)
            if _randomize_shape(probs):
                 _choose_vertical(x, y, array)
                 if True:  
                    locs.append([0,0,0,1])
    
    vals.append(_make_2d_labels(locs))

class image_gen_counter:
    _counter_ = 0

#@ future me: make this more elegant, less inputs, etc. use classes? work on this tomorrow

def generate_training_images(num_images=100,debug=0,bad_label = False, noise = 0):
    bad_locations = []
    images = []
    vals = []

    for i in range(num_images):

        if debug:
            print 'Generating image',i

        mat = np.zeros([28,28]).astype(np.float32)

        _add_multiple_shapes_to(mat, vals)

        if noise:

            generate_noise(mat, noise)

        if debug>1:
            _image(mat)
            plt.savefig('image_%04d.png' % image_gen_counter._counter_)
            plt.close()

        mat = np.reshape(mat, (784))
        images.append(mat)

        image_gen_counter._counter_ +=1

    if bad_label:
        for loc in locations:
            bad_locations.append(randomize_labels())

    if bad_label:
        return images, bad_locations
    #print locations
    return images, vals

generate_training_images()
