
from tensorflow.python.keras.models import load_model

from keras.optimizers import RMSprop

from keras.utils import to_categorical
from keras.layers import Input, Dense
from keras.models import Model

from django.shortcuts import render, redirect
import mediapipe as mp
import numpy as np
import cv2
from django.shortcuts import render
from django.http import HttpResponse, request

from yogaapp.models import RegisteredInstructor
from .models import YogaPoseData








def inFrame(lst):
    if lst[28].visibility > 0.6 and lst[27].visibility > 0.6 and lst[15].visibility>0.6 and lst[16].visibility>0.6:
        return True
    return False

def capture_pose(request):

    user_id = request.user.id
    instructor = RegisteredInstructor.objects.get(user_id=user_id)
    if request.method == 'POST':

        name = request.POST.get('asana_name')


        # Retrieve the instructor associated with the current user


        cap = cv2.VideoCapture(0)
        holistic = mp.solutions.pose
        holis = holistic.Pose()
        drawing = mp.solutions.drawing_utils
        X = []
        data_size = 0
        audio_file = request.FILES.get('audio_file')

        while True:
            lst = []
            _, frm = cap.read()
            frm = cv2.flip(frm, 1)
            res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
            if res.pose_landmarks and inFrame(res.pose_landmarks.landmark):
                for i in res.pose_landmarks.landmark:
                    lst.append(i.x - res.pose_landmarks.landmark[0].x)
                    lst.append(i.y - res.pose_landmarks.landmark[0].y)
                X.append(lst)
                data_size = data_size + 1
            else:
                cv2.putText(frm, "Make Sure Full body visible", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
            drawing.draw_landmarks(frm, res.pose_landmarks, holistic.POSE_CONNECTIONS)
            cv2.putText(frm, str(data_size), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
            cv2.imshow("window", frm)
            if cv2.waitKey(1) == 27 or data_size > 80:
                cv2.destroyAllWindows()
                cap.release()
                break
        np.save(f"{name}.npy", np.array(X))

        # Save captured pose data to the database
        data = YogaPoseData(name=name, data=X,instructor=instructor,audio_file=audio_file)
        data.save()

        # Train model with updated data
        train_model()

        return render(request, 'pose_capture.html')
    else:
        return render(request, 'pose_capture.html')




def train_model():
    # Get all pose data from database
    pose_data = YogaPoseData.objects.all()

    # Create X and y arrays
    X = []
    y = []
    label = []
    dictionary = {}
    c = 0

    # Collect pose data and labels
    for data in pose_data:
        X.extend(data.data)
        label.append(data.name)
        dictionary[data.name] = c
        c += 1

    # Convert labels to categorical format
    for label_idx in range(len(label)):
        y.extend([label_idx] * len(pose_data[label_idx].data))
    y = to_categorical(y)

    # Shuffle and split data into training and validation sets
    X = np.array(X)
    y = np.array(y)
    cnt = np.arange(X.shape[0])
    np.random.shuffle(cnt)
    X = X[cnt]
    y = y[cnt]
    split_idx = int(0.8 * len(cnt))
    X_train, y_train = X[:split_idx], y[:split_idx]
    X_val, y_val = X[split_idx:], y[split_idx:]

    # Create model architecture
    input_shape = (X_train.shape[1],)
    output_shape = len(label)
    ip = Input(shape=input_shape)
    m = Dense(128, activation="tanh")(ip)
    m = Dense(64, activation="tanh")(m)
    op = Dense(output_shape, activation="softmax")(m)
    model = Model(inputs=ip, outputs=op)
    model.compile(optimizer=RMSprop(lr=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=80)

    # Save the model and labels
    model.save("models/model.h5")
    np.save("models/labels.npy", np.array(label))




def inf(request):
    cap = cv2.VideoCapture(0)
    holistic = mp.solutions.pose
    holis = holistic.Pose()
    drawing = mp.solutions.drawing_utils
    model = load_model('models/model.h5')
    labels = np.load('models/labels.npy')
    while True:
        _, frm = cap.read()
        frm = cv2.flip(frm, 1)
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        if res.pose_landmarks and inFrame(res.pose_landmarks.landmark):
            lst = []
            for i in res.pose_landmarks.landmark:
                lst.append(i.x - res.pose_landmarks.landmark[0].x)
                lst.append(i.y - res.pose_landmarks.landmark[0].y)
            X = np.array(lst)
            pred = model.predict(X.reshape(1, -1))[0]
            label = labels[np.argmax(pred)]
            if np.max(pred) < 0.9:
                label = "Asana is not Defined"
            cv2.putText(frm, label, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
        else:
            cv2.putText(frm, "Make Sure Full body visible", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
        drawing.draw_landmarks(frm, res.pose_landmarks, holistic.POSE_CONNECTIONS)
        cv2.imshow("window", frm)
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            cap.release()
            break
    return redirect('posecollection:pose_list')



def pose_list(request):
    poses = YogaPoseData.objects.all()
    context = {'poses': poses}
    return render(request, 'pose_list.html', context)














