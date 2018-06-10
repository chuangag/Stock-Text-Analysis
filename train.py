from models import hybrid_fc_model
import keras 
from keras.utils.np_utils import to_categorical
from data_loader import *
import matplotlib.pyplot as plt
from keras.utils import plot_model
import os
from datetime import date
import shutil
import json


### Global variables
num_class=5
input_dim=82
aux_input_dim=9
configs=[]
config={'num_epochs':200,
        'batch_size':256,
        'l2_reg':0.1,
        'val_split':0.3,
        'optimizer':'rmsprop',
        'loss_weights':{'main_output': 1., 'weak_output': 0.3},
        'encoder_layers':[128,64],
        'main_layers':[64,32,32,64],
        'lr_reduce_factor':0.5
        }

# generate different model settings
for batch_size in [32,64,128,256]:
    for l2_reg in [0.01,0.02,0.05,0.1]:
        for optimizer in ['rmsprop','adam']:
            for loss_weights in [{'main_output': 1., 'weak_output': 0.1},{'main_output': 1., 'weak_output': 0.25},{'main_output': 1., 'weak_output': 0.5},{'main_output': 1., 'weak_output': 0.8}]:
                for encoder_layers in [[64],[64,64],[64,64,64],[128],[128,128]]:
                    for main_layers in [[64,64],[64,64,64],[32,32,32,32],[128,64,32],[32,32],[32,32,32]]:
                        for lr_reduce_factor in [0.1,0.5,0.8]:
                            for num_epochs in [100,200,300]:
                                config={'num_epochs':num_epochs,
                                        'batch_size':batch_size,
                                        'l2_reg':l2_reg,
                                        'val_split':0.3,
                                        'optimizer':optimizer,
                                        'loss_weights':loss_weights,
                                        'encoder_layers':encoder_layers,
                                        'main_layers':main_layers,
                                        'lr_reduce_factor':lr_reduce_factor,
                                        'verbose':0
                                        }
                                configs.append(config)
configs=[config]
for idx,config in enumerate(configs):
    today=date.today().isoformat()
    directory=f'./training_logs/{today}_train_{str(idx+1)}'
    tensordir=directory+'/tensorboard'
    checkpdir=directory+'/checkpoints'
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    os.makedirs(tensordir)
    os.makedirs(checkpdir)

    with open(directory+'/config.json','w') as f:
        json.dump(config,f,ensure_ascii=False)

    model=hybrid_fc_model(input_dim,aux_input_dim,num_class,config)
    x_cont,x_disc,labels=get_training_data('dataset_shangzheng50/')
    x_cont,x_disc,labels=shuffle_data(x_cont,x_disc,labels)
    labels=to_categorical(labels,num_classes=num_class)
    model.compile(optimizer=config['optimizer'],
                loss={'main_output': 'categorical_crossentropy', 'weak_output': 'categorical_crossentropy'},
                metrics=['categorical_accuracy'],
                loss_weights=config['loss_weights'])

    plot_model(model, to_file=f'{directory}/model.png')

    tfboard=keras.callbacks.TensorBoard(log_dir=tensordir, histogram_freq=0, write_graph=True, write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)
    checkpointer = keras.callbacks.ModelCheckpoint(filepath=checkpdir+"/weights.val_acc={val_main_output_categorical_accuracy:.3f}.hdf5", verbose=1, save_best_only=True)
    reducelr=keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=config['lr_reduce_factor'], patience=10, verbose=0, mode='auto', epsilon=0.0001, cooldown=0, min_lr=0)
    hist=model.fit({'main_input': x_disc, 'aux_input': x_cont},
            {'main_output': labels, 'weak_output': labels},
            epochs=config['num_epochs'], batch_size=config['batch_size'],verbose=config['verbose'],validation_split=config['val_split'],
            callbacks=[tfboard,checkpointer,reducelr]
            )

    plt.plot(range(num_epochs),hist.history['val_main_output_categorical_accuracy'],range(num_epochs),hist.history['main_output_categorical_accuracy'])
    plt.savefig(f'{directory}/training.png')
    plt.close()