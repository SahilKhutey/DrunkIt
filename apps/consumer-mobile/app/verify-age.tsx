import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function VerifyAgeScreen() {
  const [scanned, setScanned] = useState(false);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Scan Age Proof / License</Text>
      <Text style={styles.subtitle}>Align government ID QR code within the frame below.</Text>

      <View style={styles.cameraBox}>
        <Text style={styles.cameraPlaceholder}>[ Camera Viewfinder Placeholder ]</Text>
      </View>

      <TouchableOpacity style={styles.button} onPress={() => setScanned(true)}>
        <Text style={styles.buttonText}>Simulate ID Scan</Text>
      </TouchableOpacity>

      {scanned && (
        <View style={styles.resultBox}>
          <Text style={styles.resultTitle}>ZK Proof Generated!</Text>
          <Text style={styles.resultText}>Status: Age 21 Verified (Nullifier Hash: 0x9f8...a1b)</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 20, paddingTop: 60, alignItems: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', color: '#FFFFFF' },
  subtitle: { color: '#94A3B8', fontSize: 13, textAlign: 'center', marginVertical: 8 },
  cameraBox: { width: '100%', height: 280, backgroundColor: '#1E293B', borderRadius: 12, justifyContent: 'center', alignItems: 'center', borderStyle: 'dashed', borderWidth: 2, borderColor: '#4F46E5', marginVertical: 20 },
  cameraPlaceholder: { color: '#64748B', fontSize: 14 },
  button: { backgroundColor: '#4F46E5', borderRadius: 8, paddingVertical: 14, paddingHorizontal: 24, width: '100%', alignItems: 'center' },
  buttonText: { color: '#FFFFFF', fontWeight: '600', fontSize: 15 },
  resultBox: { marginTop: 20, backgroundColor: '#064E3B', padding: 16, borderRadius: 8, width: '100%' },
  resultTitle: { color: '#34D399', fontWeight: 'bold', fontSize: 16 },
  resultText: { color: '#A7F3D0', fontSize: 13, marginTop: 4 },
});
