import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'add_expense_screen.dart';
import 'settlement_screen.dart';

class GroupListScreen extends StatefulWidget {
  const GroupListScreen({super.key});

  @override
  State<GroupListScreen> createState() => _GroupListScreenState();
}

class _GroupListScreenState extends State<GroupListScreen> {
  List<dynamic> groups = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadGroups();
  }

  Future<void> loadGroups() async {
    try {
      final data = await ApiService.getGroups();
      setState(() {
        groups = data;
        loading = false;
      });
    } catch (_) {
      setState(() => loading = false);
    }
  }

  Future<void> showCreateGroupDialog() async {
    final ctrl = TextEditingController();

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Create Group"),
        content: TextField(
          controller: ctrl,
          decoration: const InputDecoration(labelText: "Group name"),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () async {
              if (ctrl.text.trim().isEmpty) return;

              await ApiService.createGroup(ctrl.text.trim());
              Navigator.pop(context);
              loadGroups();
            },
            child: const Text("Create"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Groups")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : groups.isEmpty
              ? const Center(child: Text("No groups yet"))
              : ListView.builder(
                  itemCount: groups.length,
                  itemBuilder: (_, i) {
                    return ListTile(
                      title: Text(groups[i]["name"]),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => SettlementScreen(
                              groupId: groups[i]["id"],
                            ),
                          ),
                        );
                      },
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: showCreateGroupDialog,
        child: const Icon(Icons.add),
      ),
    );
  }
}
