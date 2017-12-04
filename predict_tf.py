import tensorflow as tf
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

def centralize(array):
    return (array - np.mean(array, axis=0)) / np.std(array, axis=0)

input_array = pd.read_csv('process.csv', sep=',', header=None).values
predict_array = centralize(pd.read_csv('pre.csv', sep=',', header=None).values[:, 1:3])
label_data = input_array[:, :3]
input_data = centralize(input_array[:, [6, 8]])
# input_data = input_array[:, [6,  9]]
# input_data = input_array[:, 3:]
print(input_data)

# predict_data = np.vstack([input_data[:5, :],input_data[6:, :])
predict_data = input_data[4:6, :]
predict_label = label_data[4:6, :]
input_data = np.vstack([input_data[:4, :], input_data[6:, :]])
label_data = np.vstack([label_data[:4, :], label_data[6:, :]])


num_of_feature = 2
batch_size = 10
whole_data_size = 20
target_output = 3
epoch = 30001

data = tf.placeholder(tf.float32, [None, num_of_feature])
# labels = tf.placeholder(tf.float32, [None, target_output])
labels_giftcase = tf.placeholder(tf.float32, [None, 1])
labels_emerging = tf.placeholder(tf.float32, [None, 1])
labels_selftreat = tf.placeholder(tf.float32, [None, 1])



hid = tf.contrib.layers.fully_connected(data, 32, activation_fn=tf.nn.relu, normalizer_fn=tf.contrib.layers.batch_norm, weights_regularizer=tf.contrib.layers.l2_regularizer)
# hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=tf.contrib.layers.batch_norm, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=tf.contrib.layers.batch_norm, weights_regularizer=tf.contrib.layers.l2_regularizer)
output_emerging = tf.contrib.layers.fully_connected(hid, 1, activation_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
loss_emerging = tf.losses.mean_squared_error(labels_emerging, output_emerging)

hid = tf.contrib.layers.fully_connected(data, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
output_selftreat = tf.contrib.layers.fully_connected(hid, 1, activation_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
loss_selftreat = tf.losses.mean_squared_error(labels_selftreat, output_selftreat)

# hid = tf.contrib.layers.fully_connected(data, 256, activation_fn=tf.nn.relu, normalizer_fn=tf.contrib.layers.batch_norm, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(data, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
# hid = tf.contrib.layers.fully_connected(hid, 32, activation_fn=tf.nn.relu, normalizer_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
output_giftcase = tf.contrib.layers.fully_connected(hid, 1, activation_fn=None, weights_regularizer=tf.contrib.layers.l2_regularizer)
loss_giftcase = tf.losses.mean_squared_error(labels_giftcase, output_giftcase)

loss = loss_giftcase + loss_emerging + loss_selftreat
train = tf.train.AdamOptimizer(learning_rate=0.01).minimize(loss)

loss_history = []
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(epoch):
        indices = np.random.choice(whole_data_size, batch_size)
        feed_dict = {data:input_data[indices], labels_giftcase:label_data[indices, 2:3], labels_emerging:label_data[indices, 0:1], labels_selftreat:label_data[indices, 1:2]}
        # feed_dict = {data:input_data, labels:label_data}
        l2, l3, l1, _ = sess.run([loss_selftreat, loss_giftcase, loss_emerging, train], feed_dict)
        if i % 10000 == 0:
            print("loss:%f, %f, %f"%(l1, l2, l3))
    # plt.plot(loss_history)
    # plt.show()
    feed_dict = {data:predict_data}
    predict_output = sess.run([output_emerging, output_selftreat, output_giftcase], feed_dict)
    print(np.hstack(predict_output))
    print(np.sum(np.array(predict_label - predict_output) ** 2))
    feed_dict = {data:predict_array}
    predict_output = sess.run([output_emerging, output_selftreat, output_giftcase], feed_dict)
    print(np.hstack(predict_output))
