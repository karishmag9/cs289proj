import numpy as np
import os
import helper.config as config
import helper.sampling as sp
import helper.utils as utils
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.optimizers import SGD
from sklearn.cluster import KMeans

def main_dnn():
    print("starting main dnn process ...")
    raw_x, raw_y = utils.read_data("data/data_all.csv", "mood_1")
    train_x, train_y, val_x, val_y = utils.partition_data(x=raw_x, y=raw_y, ratio=0.85)
    model_list = os.listdir("model")
    model = None
    model_name = config.model_uid + ".h5"
    model_dir = "model/" + model_name
    if model_name in model_list:
        print("found previous model, recovering ...")
        model = load_model(model_dir)
        print("previous model loaded")
    else:
        print("no previous model found, constructing a new one ...")
        model = Sequential()
        feature_cnt = train_x.shape[1]
        class_cnt = train_y.shape[1]
        model.add(Dense(100, activation='relu', input_shape=(feature_cnt,)))
        model.add(Dense(500, activation='relu'))
        model.add(Dense(1000, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1000, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1000, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(500, activation='relu'))
        model.add(Dense(100, activation='relu'))
        model.add(Dense(class_cnt, activation='softmax'))
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        print("finished constructing new model")
    for i in range(config.iter_cnt):
        print("executing iteration ", str(i+1), " out of ", str(config.iter_cnt), " ... ")
        sample_x, sample_y = sp.sample_train(x=train_x, y=train_y, size=config.sample_size)
        history = model.fit(x=sample_x, y=sample_y, batch_size=config.train_batch, epochs=config.train_epochs, verbose=1)
        print("finished this round of training, saving model snapshot ...")
        model.save(model_dir)
    print("start testing ...")
    score = model.evaluate(x=val_x, y=val_y, verbose=1)
    print("final testing score is: ", score)
    print("try predicting ...")
    pred = model.predict(x=val_x, verbose=1)
    print("first 3 rows of prediction: ")
    np.set_printoptions(precision=3)
    print(pred[:3])
    print("first 3 rows of correct label: ")
    print(val_y[:3])

def main_kmean():
    print("starting main k means process ...")
    train_x, val_x, val_y = utils.read_kmeans_data("data/data_all.csv", "data/no_label_all.csv", "mood_1")
    class_cnt = val_y.shape[1]
    kmeans = KMeans(n_clusters=class_cnt, random_state=0).fit(X=train_x)
    pred = kmeans.predict(X=val_x)
    print("predicted test set: ")
    print(pred)

if __name__ == "__main__":
    try:
        if config.train_mode == "dnn":
            main_dnn()
        if config.train_mode == "kmean":
            main_kmean()
    except ValueError as err:
        for e in err.args:
            print(e)
