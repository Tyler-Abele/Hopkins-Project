// frontend/screens/HomeScreen.js
import React, { useState, useEffect } from 'react';
// Import Platform from react-native
import { StyleSheet, Text, View, Button, Alert, Platform } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
  const navigation = useNavigation();
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [prediction, setPrediction] = useState("No prediction yet");
  const [confidence, setConfidence] = useState("");
  const [vowelToRecord, setVowelToRecord] = useState("a");

  useEffect(() => {
    (async () => {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission required', 'Please grant microphone access to use this app.');
      }
    })();
  }, []);

  async function startRecording() {
    try {
      if (recording) {
        await stopRecording();
      }

      // Define a base audio mode configuration
      const audioModeConfig = {
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        // androidAudioOutput and interruptionModeAndroid will be added conditionally
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: false,
      };

      // Conditionally add Android-specific settings using Platform.OS
      if (Platform.OS === 'android') {
        audioModeConfig.androidAudioOutput = Audio.AndroidAudioOutput.SPEAKER;
        audioModeConfig.interruptionModeAndroid = Audio.AndroidInterruptionMode.DoNotMix;
      }

      await Audio.setAudioModeAsync(audioModeConfig); // Apply the platform-aware config

      console.log('Starting recording...');
      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(newRecording);
      setIsRecording(true);
      setPrediction("Recording...");
      setConfidence("");
      console.log('Recording started');

    } catch (err) {
      console.error('Failed to start recording', err);
      // More descriptive alert for debugging purposes
      Alert.alert(
        'Recording Error',
        `Failed to start recording: ${err.message}. Check browser microphone permissions.`
      );
      setIsRecording(false);
      setPrediction("Error");
    }
  }

  async function stopRecording() {
    console.log('Stopping recording...');
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
      playThroughEarpieceAndroid: true,
    });
    const uri = recording.getURI();
    console.log('Recording stopped. URI:', uri);
    setPrediction("Processing...");
    setConfidence("");
    return uri;
  }

  async function handleRecordButtonPress() {
    if (isRecording) {
      const audioUri = await stopRecording();
      if (audioUri) {
        uploadAudio(audioUri);
      }
    } else {
      startRecording();
    }
  }

  async function uploadAudio(audioUri) {
    console.log('Uploading audio from URI:', audioUri);
    setPrediction("Sending to backend..."); // Update status

    // IMPORTANT: Replace with your actual FastAPI backend URL
    // If running FastAPI locally on Windows, from WSL/web, it's typically http://localhost:8000
    // If you're on a physical Android device, you might need your computer's actual IP address
    const backendUrl = 'http://localhost:8000/predict/'; // Assuming your endpoint is /predict

    try {
      const formData = new FormData();
      // 'audio_file' must match the parameter name in your FastAPI endpoint (e.g., File(..., alias="audio_file"))
      formData.append('audio_file', {
        uri: audioUri,
        type: 'audio/m4a', // Or 'audio/wav', 'audio/aac' - match the actual recorded format
        name: 'recording.m4a', // Or '.wav', '.aac'
      });

      const response = await axios.post(backendUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Backend response:', response.data);
      if (response.data && response.data.prediction) {
        setPrediction(response.data.prediction);
        setConfidence(response.data.confidence ? `${(response.data.confidence * 100).toFixed(2)}%` : ""); // Format confidence
        Alert.alert('Prediction Received', `Prediction: ${response.data.prediction}`);
      } else {
        setPrediction("Prediction not found in response.");
        setConfidence("");
        Alert.alert('Error', 'Prediction not found in backend response.');
      }

    } catch (error) {
      console.error('Error uploading audio:', error);
      setPrediction("Error sending to backend.");
      setConfidence("");
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
        console.error("Response headers:", error.response.headers);
        Alert.alert('Backend Error', `Server responded with status ${error.response.status}: ${JSON.stringify(error.response.data)}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error("No response received:", error.request);
        Alert.alert('Network Error', 'No response from backend. Is it running at ' + backendUrl + '?');
      } else {
        // Something else happened in setting up the request
        console.error('Axios Error:', error.message);
        Alert.alert('Error', 'Could not send request: ' + error.message);
      }
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hypernasality Detector</Text>
      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Status:</Text>
        <Text style={styles.predictionText}>{prediction}</Text>
        {confidence ? <Text style={styles.confidenceText}>Confidence: {confidence}</Text> : null}
      </View>

      <View style={styles.recordButtonContainer}>
        <Button
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
          onPress={handleRecordButtonPress}
          color={isRecording ? 'red' : 'green'}
        />
      </View>

      <Text style={styles.vowelText}>Vowel to record: "{vowelToRecord}"</Text>

      <Text style={styles.instructions}>
        Press and hold the button to record the vowel "{vowelToRecord}".
        Release to stop and process.
      </Text>

      {/* Button to navigate to Details Screen */}
      <View style={styles.navigationButtonContainer}>
        <Button
          title="Go to Details"
          onPress={() => navigation.navigate('Details')}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#333',
  },
  statusContainer: {
    marginBottom: 20,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 18,
    color: '#666',
    marginBottom: 5,
  },
  predictionText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 5,
  },
  confidenceText: {
    fontSize: 16,
    color: '#555',
  },
  recordButtonContainer: {
    marginVertical: 30,
    width: '60%',
  },
  vowelText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#333',
  },
  instructions: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
    color: '#777',
    maxWidth: '80%',
  },
  navigationButtonContainer: {
    marginTop: 20,
  }
});