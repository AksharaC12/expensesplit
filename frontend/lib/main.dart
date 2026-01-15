import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const ExpenseSplitApp());
}

class ExpenseSplitApp extends StatelessWidget {
  const ExpenseSplitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Expense Split',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: LoginScreen(),
    );
  }
}
