import os
from options.test_options import TestOptions
from options.test_options import BaseOptions
from data import CreateDataLoader
from models import create_model
from util.visualizer import save_images
from util import html


def run(data_root, pretrain_model, result_dir, model):
    
    opt = TestOptions().parse()
    opt.dataroot = data_root
    results_dir = result_dir #s 글자 한 개로 변수 이름 다르니까 주의!
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    name = model[1]
    model = model[0]
    # create a website
    web_dir = os.path.join(results_dir)
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (name, opt.phase, opt.epoch))
    # test with eval mode. This only affects layers like batchnorm and dropout.
    # pix2pix: we use batchnorm and dropout in the original pix2pix. You can experiment it with and without eval() mode.
    # CycleGAN: It should not affect CycleGAN as CycleGAN uses instancenorm without dropout.
    if opt.eval:
        model.eval()
    # cityscape icin eklendi.
    if opt.cityscapes:
        with open(opt.cityscape_fnames) as f:
            f_names = f.read().split('\n')

    for i, data in enumerate(dataset):
        if i >= opt.num_test:
            break
        model.set_input(data)
        model.test()
        visuals = model.get_current_visuals()
        img_path = model.get_image_paths()
        if opt.cityscapes:
            index = int(os.path.basename(img_path[0]).split("_")[0]) - 1  # cityscapes
        if i % 5 == 0:
            print('processing (%04d)-th image... %s' % (i, img_path))
            #img_path = 'upload/[user_id]/[upload_file]
        if not opt.cityscapes:
            image_list = save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize, citysc=False)
        else:
            image_list = save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize,
                        f_name=f_names[index], citysc=True)  # cityscapes
    # save the website
    webpage.save()
    return image_list
