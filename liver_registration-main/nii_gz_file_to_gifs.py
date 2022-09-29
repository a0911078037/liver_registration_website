import matplotlib.pyplot as plt
import nibabel as nib
import os
import base64


def create_gif(file_path, title='result', filename='test.gif'):
    import matplotlib.animation as animate
    if os.path.exists('seg.gif'):
        os.remove('seg.gif')
    input_image = nib.load(file_path)
    images = []
    input_image_data = input_image.get_fdata()
    fig = plt.figure()
    for i in range(len(input_image_data)):
        im = plt.imshow(input_image_data[i], animated=True)
        images.append([im])

    ani = animate.ArtistAnimation(fig, images, interval=25, blit=True, repeat_delay=500)
    plt.title(title, fontsize=20)
    plt.axis('off')
    ani.save(filename)


if __name__ == '__main__':
    file = open('seg.gif', 'rb')
    file_base64 = f'data:image/gif;base64,{base64.b64encode(file.read()).decode()}'
    print(file_base64)