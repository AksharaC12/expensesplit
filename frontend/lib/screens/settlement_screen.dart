import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SettlementScreen extends StatefulWidget {
  final int groupId;
  const SettlementScreen({super.key, required this.groupId});

  @override
  State<SettlementScreen> createState() => _SettlementScreenState();
}

class _SettlementScreenState extends State<SettlementScreen> {
  Map<String, dynamic> balances = {};
  bool loading = true;

  Future<void> load() async {
    final data = await ApiService.getBalances(widget.groupId);
    setState(() {
      balances = Map<String, dynamic>.from(data);
      loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Settlement")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : balances.isEmpty
              ? const Center(child: Text("No balances to settle"))
              : Column(
                  children: [
                    Expanded(
                      child: ListView(
                        children: balances.entries.map((e) {
                          return ListTile(
                            title: Text(e.key),
                            trailing: Text(
                              e.value.toStringAsFixed(2),
                              style: TextStyle(
                                color: e.value >= 0 ? Colors.green : Colors.red,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                    ElevatedButton(
                      onPressed: () async {
                        await ApiService.settleGroup(widget.groupId);
                        Navigator.pop(context);
                      },
                      child: const Text("Settle Up"),
                    ),
                  ],
                ),
    );
  }
}
