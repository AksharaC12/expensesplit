import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const ExpenseSplitApp());
}

class ExpenseSplitApp extends StatelessWidget {
  const ExpenseSplitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'ExpenseSplit',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        scaffoldBackgroundColor: Colors.white,
        useMaterial3: true,
      ),
      home: const SplashScreen(), // 👈 Splash first
    );
  }
}
