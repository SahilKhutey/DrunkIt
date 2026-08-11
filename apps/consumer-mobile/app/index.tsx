import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';

export default function HomeScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.badge}>FACCP Regulated Commerce</Text>
        <Text style={styles.title}>Alcohol Delivery & Compliance</Text>
        <Text style={styles.subtitle}>Verified, legal, and age-gated delivery in your state.</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Identity & Age Status</Text>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Age Verification (C1):</Text>
          <Text style={styles.statusValueVerified}>VERIFIED 21+</Text>
        </View>
        <TouchableOpacity style={styles.buttonSecondary}>
          <Text style={styles.buttonTextSecondary}>View ZK Age Token</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Quick Actions</Text>
        <TouchableOpacity style={styles.buttonPrimary}>
          <Text style={styles.buttonTextPrimary}>Browse Nearby Licensed Stores</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.buttonPrimary, { marginTop: 10 }]}>
          <Text style={styles.buttonTextPrimary}>Scan ID / Age Proof QR</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { padding: 20, paddingTop: 60 },
  header: { marginBottom: 24 },
  badge: { color: '#6366F1', fontWeight: '700', textTransform: 'uppercase', fontSize: 12, marginBottom: 6 },
  title: { fontSize: 26, fontWeight: 'bold', color: '#FFFFFF' },
  subtitle: { color: '#94A3B8', fontSize: 14, marginTop: 4 },
  card: { backgroundColor: '#1E293B', borderRadius: 12, padding: 18, marginBottom: 16, borderAttributes: 1, borderColor: '#334155' },
  cardTitle: { color: '#F8FAFC', fontSize: 18, fontWeight: '600', marginBottom: 12 },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  statusLabel: { color: '#94A3B8', fontSize: 14 },
  statusValueVerified: { color: '#10B981', fontWeight: 'bold', fontSize: 14 },
  buttonPrimary: { backgroundColor: '#4F46E5', borderRadius: 8, paddingVertical: 14, alignItems: 'center' },
  buttonTextPrimary: { color: '#FFFFFF', fontWeight: '600', fontSize: 15 },
  buttonSecondary: { backgroundColor: '#334155', borderRadius: 8, paddingVertical: 10, alignItems: 'center' },
  buttonTextSecondary: { color: '#CBD5E1', fontWeight: '500', fontSize: 14 },
});
