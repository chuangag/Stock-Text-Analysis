import keras
from keras.layers import Input, Dense
from keras.models import Model
from keras import regularizers

def hybrid_fc_model(input_dim,aux_input_dim,num_class,config):
    reg=config['l2_reg']
    main_input = Input(shape=(input_dim,), dtype='float32', name='main_input')
    assert(len(config['encoder_layers'])>0)
    assert(len(config['main_layers'])>0)
    x = Dense(config['encoder_layers'][0], activation='relu',kernel_regularizer=regularizers.l2(reg))(main_input)
    for n_node in config['encoder_layers'][1:]:
        x = Dense(n_node, activation='relu',kernel_regularizer=regularizers.l2(reg))(x)

    weak_output = Dense(num_class, activation='softmax', name='weak_output')(x) # only with discrete data

    auxiliary_input = Input(shape=(aux_input_dim,), name='aux_input')

    x = keras.layers.concatenate([x, auxiliary_input])
    x = Dense(config['main_layers'][0], activation='relu',kernel_regularizer=regularizers.l2(reg))(x)
    for n_node in config['main_layers'][1:]:
        x = Dense(n_node, activation='relu',kernel_regularizer=regularizers.l2(reg))(x)
    main_output = Dense(num_class, activation='softmax', name='main_output')(x)

    model = Model(inputs=[main_input, auxiliary_input], outputs=[main_output, weak_output])
    
    return model

