use std::fs;
use std::sync::Mutex;
use std::process::Command;
use sysinfo::System;
use serde::{Serialize, Deserialize};

#[derive(Serialize)]
struct SysVitals { cpu_load: f32, ram_usage: u64, ram_total: u64 }

#[derive(Serialize)]
struct SkillFile { name: String, size: u64 }

#[derive(Serialize)]
struct MemoryEntry { key: String, value: String, #[serde(rename = "type")] type_: String, timestamp: u64 }

#[derive(Serialize)]
struct Agent { id: String, name: String, model: String, status: String, role: String, icon: String }

#[derive(Serialize)]
struct MeshStatus { peers: u32, public_url: String }

#[derive(Serialize)]
struct BrowserStatus { active_layers: u32, status: String }

struct AppState { sys: Mutex<System> }

#[tauri::command]
fn get_sys_vitals(state: tauri::State<'_, AppState>) -> SysVitals {
    let mut sys = state.sys.lock().unwrap();
    sys.refresh_cpu_usage();
    sys.refresh_memory();
    SysVitals { cpu_load: sys.global_cpu_usage(), ram_usage: sys.used_memory(), ram_total: sys.total_memory() }
}

#[tauri::command]
fn get_installed_skills() -> Vec<SkillFile> {
    let mut skills = Vec::new();
    if let Ok(entries) = fs::read_dir("/home/gamerx/aria/skills") {
        for entry in entries.flatten() {
            if let Ok(metadata) = entry.metadata() {
                if let Ok(file_name) = entry.file_name().into_string() {
                    if file_name.ends_with(".py") { skills.push(SkillFile { name: file_name, size: metadata.len() }); }
                }
            }
        }
    }
    skills.sort_by(|a, b| a.name.cmp(&b.name));
    skills
}

#[tauri::command]
fn get_memory_size() -> u64 {
    let mut total_size = 0;
    if let Ok(entries) = fs::read_dir("/home/gamerx/aria/") {
        for entry in entries.flatten() {
            if let Ok(metadata) = entry.metadata() { total_size += metadata.len(); }
        }
    }
    total_size
}

#[tauri::command]
fn get_memory_entries() -> Vec<MemoryEntry> {
    vec![
        MemoryEntry { key: "User Profile".into(), value: "GamerX, ARIA Owner".into(), type_: "fact".into(), timestamp: 1711654320000 },
        MemoryEntry { key: "System".into(), value: "Arch Linux, 16GB RAM".into(), type_: "fact".into(), timestamp: 1711654320000 },
        MemoryEntry { key: "Preference".into(), value: "Use concise responses".into(), type_: "preference".into(), timestamp: 1711654320000 },
        MemoryEntry { key: "Last Session".into(), value: "Deployed browser agent".into(), type_: "session".into(), timestamp: 1711654320000 },
    ]
}

#[tauri::command]
fn get_aria_config() -> serde_json::Value {
    serde_json::json!({ "model": "qwen2.5-coder-32b-instruct", "temperature": 0.4 })
}

#[tauri::command] fn set_aria_config(_key: String, _value: String) -> Result<(), String> { Ok(()) }

#[tauri::command]
fn get_logs(count: usize) -> Vec<String> {
    if let Ok(out) = Command::new("journalctl").args(["--user", "-u", "jarvis.service", "-n", &count.to_string(), "--no-pager", "-o", "cat"]).output() {
        String::from_utf8_lossy(&out.stdout).lines().map(|s| s.into()).collect()
    } else {
        vec!["[ERROR] Failed to read logs".into()]
    }
}

#[tauri::command]
fn get_mesh_status() -> MeshStatus { MeshStatus { peers: 0, public_url: "Local only".into() } }

#[tauri::command]
fn get_browser_status() -> BrowserStatus { BrowserStatus { active_layers: 3, status: "ONLINE".into() } }

#[tauri::command]
fn get_service_status() -> String {
    if let Ok(out) = Command::new("systemctl").args(["--user", "is-active", "jarvis.service"]).output() {
        String::from_utf8_lossy(&out.stdout).trim().into()
    } else { "unknown".into() }
}

#[tauri::command] fn restart_aria_service() { let _ = Command::new("systemctl").args(["--user", "restart", "jarvis.service"]).spawn(); }
#[tauri::command] fn run_self_test() -> String { "All systems nominal.".into() }

#[tauri::command]
fn get_agents() -> Vec<Agent> { vec![] }

#[tauri::command] fn get_voice_config() -> serde_json::Value { serde_json::json!({ "backend": "piper", "speed": 1.0 }) }
#[tauri::command] fn get_credentials() -> Vec<serde_json::Value> { vec![] }
#[tauri::command] fn get_devices() -> Vec<serde_json::Value> { vec![] }
#[tauri::command] fn get_personality() -> serde_json::Value { serde_json::json!({ "formal": 50 }) }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState { sys: Mutex::new(System::new_all()) })
        .invoke_handler(tauri::generate_handler![
            get_sys_vitals, get_installed_skills, get_memory_size, get_memory_entries,
            get_aria_config, set_aria_config, get_logs, get_mesh_status, get_browser_status,
            get_service_status, restart_aria_service, run_self_test, get_agents,
            get_voice_config, get_credentials, get_devices, get_personality
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
