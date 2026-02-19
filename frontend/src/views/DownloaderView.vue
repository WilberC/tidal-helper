<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import axios from "axios";
import { useToast } from "vue-toastification";

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

interface DownloaderItem {
  id: number;
  user_id: number;
  tidal_id: string;
  name: string;
  item_type: string; // "playlist" | "mix"
  status: string; // "pending" | "downloaded" | "not_wanted"
  position: number;
  created_at: string;
}

const API = import.meta.env.VITE_API_URL;

function authHeaders() {
  return { Authorization: `Bearer ${authStore.token}` };
}

// ── State ────────────────────────────────────────────────────────────────────

const allItems = ref<DownloaderItem[]>([]);
const isLoading = ref(false);
const isPopulating = ref(false);

// Info modal
const infoItem = ref<DownloaderItem | null>(null);

// ── Selection ─────────────────────────────────────────────────────────────────

// Using an array for Vue reactivity (easier than manually managing Set reactivity)
const selectedIds = ref<number[]>([]);
const anchorId = ref<number | null>(null);
const anchorStatus = ref<string | null>(null);

function isSelected(id: number) {
  return selectedIds.value.includes(id);
}

function selectedInColumn(status: string) {
  return getColumnItems(status).filter((i) => isSelected(i.id));
}

function clearSelection() {
  selectedIds.value = [];
  anchorId.value = null;
  anchorStatus.value = null;
}

function isAllSelectedInColumn(status: string) {
  const colItems = getColumnItems(status);
  if (colItems.length === 0) return false;
  return colItems.every((i) => isSelected(i.id));
}

function toggleSelectAllInColumn(status: string) {
  const colItems = getColumnItems(status);
  if (isAllSelectedInColumn(status)) {
    const colIds = new Set(colItems.map((i) => i.id));
    selectedIds.value = selectedIds.value.filter((id) => !colIds.has(id));
  } else {
    const next = new Set([...selectedIds.value, ...colItems.map((i) => i.id)]);
    selectedIds.value = [...next];
  }
}

function moveSelectedToColumn(targetStatus: string) {
  if (selectedIds.value.length === 0) return;
  const idsToMove = new Set(selectedIds.value);
  const itemsToMove = allItems.value.filter((i) => idsToMove.has(i.id));
  const affectedSrcStatuses = new Set(itemsToMove.map((i) => i.status).filter((s) => s !== targetStatus));

  // Update status
  itemsToMove.forEach((item) => { item.status = targetStatus; });

  // Reassign target column positions (append moved items at the end)
  const targetColItems = allItems.value
    .filter((i) => i.status === targetStatus)
    .sort((a, b) => a.position - b.position);
  targetColItems.forEach((item, idx) => { item.position = idx; });

  // Reassign affected source columns
  affectedSrcStatuses.forEach((srcStatus) => {
    const srcColItems = allItems.value
      .filter((i) => i.status === srcStatus)
      .sort((a, b) => a.position - b.position);
    srcColItems.forEach((item, idx) => { item.position = idx; });
  });

  // Trigger reactivity
  allItems.value = [...allItems.value];

  const colLabel = columns.find((c) => c.status === targetStatus)?.label ?? targetStatus;
  const count = idsToMove.size;
  clearSelection();
  toast.success(`Moved ${count} item${count > 1 ? "s" : ""} to ${colLabel}`);
  saveBulkPositions();
}

function handleItemClick(event: MouseEvent, item: DownloaderItem, colStatus: string) {
  if (event.shiftKey && anchorId.value !== null && anchorStatus.value === colStatus) {
    // Range select within the same column — never copies
    const colItems = getColumnItems(colStatus);
    const anchorIdx = colItems.findIndex((i) => i.id === anchorId.value);
    const currentIdx = colItems.findIndex((i) => i.id === item.id);
    if (anchorIdx !== -1 && currentIdx !== -1) {
      const start = Math.min(anchorIdx, currentIdx);
      const end = Math.max(anchorIdx, currentIdx);
      const rangeIds = colItems.slice(start, end + 1).map((i) => i.id);
      // Merge range into current selection (don't reset it)
      const next = new Set([...selectedIds.value, ...rangeIds]);
      selectedIds.value = [...next];
    }
  } else if (event.ctrlKey || event.metaKey) {
    // Toggle individual item
    if (isSelected(item.id)) {
      selectedIds.value = selectedIds.value.filter((id) => id !== item.id);
    } else {
      selectedIds.value = [...selectedIds.value, item.id];
      anchorId.value = item.id;
      anchorStatus.value = colStatus;
    }
  } else {
    // Plain click: copy short path + set anchor + clear selection
    clearSelection();
    anchorId.value = item.id;
    anchorStatus.value = colStatus;
    copyToClipboard(shortPath(item), `Copied: ${shortPath(item)}`);
  }
}

function onEscape(e: KeyboardEvent) {
  if (e.key === "Escape") clearSelection();
}

// ── Copy-all settings ─────────────────────────────────────────────────────────

type CopyFormat = "short" | "full";
const copyFormat = ref<CopyFormat>("short");
// separator string — the input is the source of truth; preset chips just fill it
const separator = ref(" ");

const PRESETS: { label: string; char: string; title: string }[] = [
  { label: "Space", char: " ", title: "Single space" },
  { label: ",", char: ",", title: "Comma" },
  { label: ";", char: ";", title: "Semicolon" },
  { label: "↵", char: "\n", title: "New line" },
];

// Which preset chip is currently active (matches separator value exactly)
const activePreset = computed(() =>
  PRESETS.find((p) => p.char === separator.value)?.char ?? null
);

function setPreset(char: string) {
  separator.value = char;
}

// ── Computed columns ─────────────────────────────────────────────────────────

const columns: { label: string; status: string; color: string; headerColor: string; accentFlash: string }[] = [
  {
    label: "Pending",
    status: "pending",
    color: "border-yellow-500/40",
    headerColor: "text-yellow-400",
    accentFlash: "ring-yellow-400/50",
  },
  {
    label: "Downloading",
    status: "downloading",
    color: "border-blue-500/40",
    headerColor: "text-blue-400",
    accentFlash: "ring-blue-400/50",
  },
  {
    label: "Downloaded",
    status: "downloaded",
    color: "border-green-500/40",
    headerColor: "text-green-400",
    accentFlash: "ring-green-400/50",
  },
  {
    label: "Not Wanted",
    status: "not_wanted",
    color: "border-red-500/40",
    headerColor: "text-red-400",
    accentFlash: "ring-red-400/50",
  },
];

const pending = computed(() =>
  allItems.value.filter((i) => i.status === "pending").sort((a, b) => a.position - b.position)
);
const downloaded = computed(() =>
  allItems.value.filter((i) => i.status === "downloaded").sort((a, b) => a.position - b.position)
);
const downloading = computed(() =>
  allItems.value.filter((i) => i.status === "downloading").sort((a, b) => a.position - b.position)
);
const not_wanted = computed(() =>
  allItems.value.filter((i) => i.status === "not_wanted").sort((a, b) => a.position - b.position)
);

function getColumnItems(status: string): DownloaderItem[] {
  if (status === "pending") return pending.value;
  if (status === "downloaded") return downloaded.value;
  if (status === "downloading") return downloading.value;
  return not_wanted.value;
}

// ── API helpers ───────────────────────────────────────────────────────────────

async function fetchItems() {
  isLoading.value = true;
  try {
    const res = await axios.get<DownloaderItem[]>(`${API}/api/v1/downloader/`, {
      headers: authHeaders(),
    });
    allItems.value = res.data;
  } catch (e) {
    toast.error("Failed to load downloader items");
  } finally {
    isLoading.value = false;
  }
}

async function populate() {
  isPopulating.value = true;
  try {
    const res = await axios.post<DownloaderItem[]>(`${API}/api/v1/downloader/populate`, {}, {
      headers: authHeaders(),
    });
    allItems.value = res.data;
    toast.success("Populated from your playlists & mixes!");
  } catch (e) {
    toast.error("Failed to populate");
  } finally {
    isPopulating.value = false;
  }
}

async function saveBulkPositions() {
  const updates = allItems.value.map((item) => ({
    id: item.id,
    status: item.status,
    position: item.position,
  }));
  try {
    await axios.put(`${API}/api/v1/downloader/bulk-update`, updates, {
      headers: authHeaders(),
    });
  } catch (e) {
    toast.error("Failed to save order");
  }
}

async function deleteItem(item: DownloaderItem) {
  try {
    await axios.delete(`${API}/api/v1/downloader/${item.id}`, {
      headers: authHeaders(),
    });
    allItems.value = allItems.value.filter((i) => i.id !== item.id);
    toast.success("Removed");
  } catch (e) {
    toast.error("Failed to remove item");
  }
}

// ── Clipboard ─────────────────────────────────────────────────────────────────

function shortPath(item: DownloaderItem) {
  return `${item.item_type}/${item.tidal_id}`;
}

function longUrl(item: DownloaderItem) {
  return `https://tidal.com/${item.item_type}/${item.tidal_id}`;
}

function itemUrl(item: DownloaderItem) {
  return copyFormat.value === "short" ? shortPath(item) : longUrl(item);
}

function copyToClipboard(text: string, label = "Copied!") {
  navigator.clipboard.writeText(text).then(() => {
    toast.success(label);
  });
}

// flash state per column (to give visual feedback on "Copy All")
const flashingCol = ref<string | null>(null);

function copyColumnItems(status: string) {
  const sel = selectedInColumn(status);
  const items = sel.length > 0 ? sel : getColumnItems(status);
  if (items.length === 0) {
    toast.warning("Nothing to copy — column is empty");
    return;
  }
  const sep = separator.value === "" ? " " : separator.value;
  const text = items.map(itemUrl).join(sep);
  navigator.clipboard.writeText(text).then(() => {
    const colLabel = columns.find((c) => c.status === status)?.label ?? status;
    const fmt = copyFormat.value === "short" ? "short" : "full";
    const scope = sel.length > 0 ? `${items.length} selected` : `all ${items.length}`;
    toast.success(`Copied ${scope} ${fmt} URL${items.length > 1 ? "s" : ""} from ${colLabel}`);
    flashingCol.value = status;
    setTimeout(() => { flashingCol.value = null; }, 600);
  });
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────

const draggedItem = ref<DownloaderItem | null>(null);
const draggedFromStatus = ref<string | null>(null);
const dragOverItemId = ref<number | null>(null);
const dragOverStatus = ref<string | null>(null);
const dragOverAfter = ref(false); // insert after (true) or before (false) the hovered item

function startDrag(event: DragEvent, item: DownloaderItem, fromStatus: string) {
  draggedItem.value = item;
  draggedFromStatus.value = fromStatus;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", String(item.id));
  }
}

function onItemDragOver(event: DragEvent, item: DownloaderItem, colStatus: string) {
  event.preventDefault();
  dragOverStatus.value = colStatus;
  dragOverItemId.value = item.id;
  if (event.currentTarget instanceof HTMLElement) {
    const rect = event.currentTarget.getBoundingClientRect();
    dragOverAfter.value = event.clientY > rect.top + rect.height / 2;
  }
}

function onColumnDragOver(event: DragEvent, colStatus: string) {
  event.preventDefault();
  dragOverStatus.value = colStatus;
  if (dragOverItemId.value !== null) {
    const colItems = getColumnItems(colStatus);
    const overItem = colItems.find((i) => i.id === dragOverItemId.value);
    if (!overItem) {
      dragOverItemId.value = null;
    }
  }
}

function onDrop(event: DragEvent, targetStatus: string, targetItemId: number | null) {
  event.preventDefault();
  if (!draggedItem.value) return;

  const src = draggedItem.value;

  // If dragging a selected item, move ALL selected items together
  if (isSelected(src.id) && selectedIds.value.length > 1) {
    const idsToMove = new Set(selectedIds.value);
    // Preserve relative order of moved items
    const itemsToMove = allItems.value
      .filter((i) => idsToMove.has(i.id))
      .sort((a, b) => a.position - b.position);
    const affectedSrcStatuses = new Set(
      itemsToMove.map((i) => i.status).filter((s) => s !== targetStatus)
    );

    // Work with remaining items (not being moved)
    const remaining = allItems.value.filter((i) => !idsToMove.has(i.id));

    // Calculate insert position within the remaining target-column items
    const targetColItems = remaining
      .filter((i) => i.status === targetStatus)
      .sort((a, b) => a.position - b.position);

    let insertAt = targetColItems.length; // default: end
    // Only use targetItemId as anchor if it's not one of the items being moved
    if (targetItemId !== null && !idsToMove.has(targetItemId)) {
      const targetIdx = targetColItems.findIndex((i) => i.id === targetItemId);
      if (targetIdx !== -1) {
        insertAt = dragOverAfter.value ? targetIdx + 1 : targetIdx;
      }
    }

    // Update status and splice in
    itemsToMove.forEach((item) => { item.status = targetStatus; });
    targetColItems.splice(insertAt, 0, ...itemsToMove);
    targetColItems.forEach((item, idx) => { item.position = idx; });

    // Reassign affected source columns
    affectedSrcStatuses.forEach((s) => {
      remaining
        .filter((i) => i.status === s)
        .sort((a, b) => a.position - b.position)
        .forEach((item, idx) => { item.position = idx; });
    });

    allItems.value = [
      ...remaining.filter((i) => i.status !== targetStatus),
      ...targetColItems,
    ];

    clearSelection();
    draggedItem.value = null;
    draggedFromStatus.value = null;
    dragOverItemId.value = null;
    dragOverStatus.value = null;
    saveBulkPositions();
    return;
  }

  // Single-item drag (original behaviour)
  const srcStatus = draggedFromStatus.value!;

  const srcIndex = allItems.value.findIndex((i) => i.id === src.id);
  if (srcIndex !== -1) allItems.value.splice(srcIndex, 1);

  src.status = targetStatus;

  const targetColItems = allItems.value
    .filter((i) => i.status === targetStatus)
    .sort((a, b) => a.position - b.position);

  let insertAt = targetColItems.length;
  if (targetItemId !== null) {
    const targetIdx = targetColItems.findIndex((i) => i.id === targetItemId);
    if (targetIdx !== -1) {
      insertAt = dragOverAfter.value ? targetIdx + 1 : targetIdx;
    }
  }

  targetColItems.splice(insertAt, 0, src);
  targetColItems.forEach((item, idx) => { item.position = idx; });

  const otherItems = allItems.value.filter((i) => i.status !== targetStatus);
  allItems.value = [...otherItems, ...targetColItems];

  if (srcStatus !== targetStatus) {
    allItems.value
      .filter((i) => i.status === srcStatus)
      .sort((a, b) => a.position - b.position)
      .forEach((item, idx) => { item.position = idx; });
  }

  draggedItem.value = null;
  draggedFromStatus.value = null;
  dragOverItemId.value = null;
  dragOverStatus.value = null;
  saveBulkPositions();
}

function endDrag() {
  draggedItem.value = null;
  draggedFromStatus.value = null;
  dragOverItemId.value = null;
  dragOverStatus.value = null;
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

onMounted(() => {
  fetchItems();
  window.addEventListener("keydown", onEscape);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onEscape);
});
</script>

<template>
  <div class="p-6 bg-gray-900 min-h-screen text-white">
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
      <div class="flex items-center gap-4">
        <button
          @click="router.push('/')"
          class="text-gray-400 hover:text-white transition"
          title="Back to Dashboard"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 class="text-3xl font-bold text-cyan-400">Playlist Downloader Manager</h1>
      </div>
      <button
        @click="populate"
        :disabled="isPopulating"
        class="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2 px-5 rounded transition flex items-center gap-2"
        title="Populate from your Tidal playlists & mixes"
      >
        <svg v-if="isPopulating" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{{ isPopulating ? "Populating..." : "Populate from Tidal" }}</span>
      </button>
    </div>

    <!-- ── Copy-all settings bar ──────────────────────────────────────────── -->
    <div class="flex flex-wrap items-center gap-x-6 gap-y-3 mb-6 bg-gray-800/60 border border-white/8 rounded-xl px-5 py-3">
      <!-- Format toggle -->
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-400 uppercase tracking-wide font-semibold shrink-0">Format</span>
        <div class="flex rounded-lg overflow-hidden border border-gray-700">
          <button
            @click="copyFormat = 'short'"
            :class="[
              'px-3 py-1 text-sm font-medium transition',
              copyFormat === 'short'
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700',
            ]"
          >Short</button>
          <button
            @click="copyFormat = 'full'"
            :class="[
              'px-3 py-1 text-sm font-medium transition',
              copyFormat === 'full'
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700',
            ]"
          >Full URL</button>
        </div>
      </div>

      <!-- Divider -->
      <div class="h-5 w-px bg-gray-700 hidden sm:block"></div>

      <!-- Separator -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs text-gray-400 uppercase tracking-wide font-semibold shrink-0">Separator</span>

        <!-- Preset chips -->
        <div class="flex gap-1">
          <button
            v-for="preset in PRESETS"
            :key="preset.char"
            @click="setPreset(preset.char)"
            :title="preset.title"
            :class="[
              'px-2.5 py-1 text-sm rounded-md border transition font-mono',
              activePreset === preset.char
                ? 'border-cyan-500 bg-cyan-600/20 text-cyan-300'
                : 'border-gray-600 bg-gray-800 text-gray-400 hover:border-gray-400 hover:text-white',
            ]"
          >{{ preset.label }}</button>
        </div>

        <!-- Custom input -->
        <div class="flex items-center gap-1.5">
          <span class="text-xs text-gray-600">or</span>
          <input
            v-model="separator"
            type="text"
            maxlength="10"
            placeholder="custom…"
            class="w-24 bg-gray-900 border border-gray-600 rounded-md px-2 py-1 text-sm text-white font-mono placeholder-gray-600 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      <!-- Preview -->
      <div class="ml-auto shrink-0 text-xs text-gray-500">
        Preview:
        <code class="text-gray-300 bg-gray-900 rounded px-1.5 py-0.5 font-mono ml-1">
          {{ copyFormat === 'short' ? 'playlist/abc123' : 'https://tidal.com/playlist/abc123' }}
        </code>
      </div>
    </div>

    <!-- Selection action bar -->
    <div
      v-if="selectedIds.length > 0"
      class="flex flex-wrap items-center gap-x-4 gap-y-2 mb-4 bg-cyan-900/20 border border-cyan-500/30 rounded-xl px-4 py-2.5"
    >
      <span class="text-sm text-cyan-300 font-semibold shrink-0">
        {{ selectedIds.length }} item{{ selectedIds.length > 1 ? "s" : "" }} selected
      </span>
      <div class="h-4 w-px bg-gray-600 hidden sm:block"></div>
      <span class="text-xs text-gray-400 shrink-0">Move to:</span>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="col in columns"
          :key="col.status"
          @click="moveSelectedToColumn(col.status)"
          :class="[
            'text-xs px-3 py-1 rounded-lg border transition font-medium',
            col.headerColor,
            col.color.replace('border-', 'border-').replace('/40', '/60'),
            'hover:bg-white/10',
          ]"
        >
          {{ col.label }}
        </button>
      </div>
      <button
        @click="clearSelection()"
        class="ml-auto text-xs text-gray-500 hover:text-white transition shrink-0"
      >
        Clear
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
    </div>

    <!-- Kanban Board -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <div
        v-for="col in columns"
        :key="col.status"
        class="flex flex-col"
        @dragover="onColumnDragOver($event, col.status)"
        @drop="onDrop($event, col.status, null)"
      >
        <!-- Column header -->
        <div class="flex items-center justify-between mb-3 px-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h2 :class="['text-lg font-bold', col.headerColor]">{{ col.label }}</h2>
            <span class="text-xs bg-gray-700 text-gray-300 rounded-full px-2 py-0.5">
              {{ getColumnItems(col.status).length }}
            </span>
            <!-- Selected badge -->
            <span
              v-if="selectedInColumn(col.status).length > 0"
              class="text-xs bg-cyan-600/30 text-cyan-300 border border-cyan-500/40 rounded-full px-2 py-0.5 flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              {{ selectedInColumn(col.status).length }} selected
            </span>
            <!-- Select all toggle -->
            <button
              @click="toggleSelectAllInColumn(col.status)"
              :disabled="getColumnItems(col.status).length === 0"
              :title="isAllSelectedInColumn(col.status) ? 'Deselect all in column' : 'Select all in column'"
              :class="[
                'text-xs px-2 py-0.5 rounded-md border transition',
                isAllSelectedInColumn(col.status)
                  ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10'
                  : 'border-gray-600 text-gray-500 hover:border-gray-400 hover:text-gray-300',
                getColumnItems(col.status).length === 0 ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer',
              ]"
            >
              {{ isAllSelectedInColumn(col.status) ? "Deselect all" : "Select all" }}
            </button>
          </div>

          <!-- Copy button -->
          <button
            @click="copyColumnItems(col.status)"
            :disabled="getColumnItems(col.status).length === 0"
            :title="selectedInColumn(col.status).length > 0
              ? `Copy ${selectedInColumn(col.status).length} selected URLs`
              : `Copy all ${col.label} URLs`"
            :class="[
              'flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg border transition',
              getColumnItems(col.status).length === 0
                ? 'border-gray-700 text-gray-600 cursor-not-allowed'
                : selectedInColumn(col.status).length > 0
                  ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20'
                  : 'border-gray-600 text-gray-400 hover:border-cyan-500 hover:text-cyan-400 hover:bg-cyan-500/10',
              flashingCol === col.status ? 'border-cyan-400 text-cyan-400 bg-cyan-500/10' : '',
            ]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            {{ selectedInColumn(col.status).length > 0
              ? `Copy ${selectedInColumn(col.status).length} selected`
              : 'Copy all' }}
          </button>
        </div>

        <!-- Drop zone -->
        <div
          :class="[
            'flex-1 min-h-32 rounded-xl border-2 border-dashed p-3 flex flex-col gap-2 transition-all',
            col.color,
            dragOverStatus === col.status && draggedItem && !dragOverItemId
              ? 'bg-white/5'
              : 'bg-gray-800/40',
            flashingCol === col.status ? 'ring-2 ' + col.accentFlash : '',
          ]"
        >
          <!-- Empty state -->
          <div
            v-if="getColumnItems(col.status).length === 0"
            class="flex-1 flex items-center justify-center text-gray-600 text-sm select-none"
          >
            Drop items here
          </div>

          <!-- Items -->
          <div
            v-for="item in getColumnItems(col.status)"
            :key="item.id"
            draggable="true"
            @dragstart="startDrag($event, item, col.status)"
            @dragover="onItemDragOver($event, item, col.status)"
            @drop.stop="onDrop($event, col.status, item.id)"
            @dragend="endDrag"
            @click.stop="handleItemClick($event, item, col.status)"
            :class="[
              'group relative border rounded-lg p-3 cursor-pointer select-none transition-all',
              (draggedItem?.id === item.id || (draggedItem && isSelected(draggedItem.id) && isSelected(item.id)))
                ? 'opacity-40 border-gray-600 bg-gray-800'
                : isSelected(item.id)
                  ? 'bg-cyan-900/30 border-cyan-500/70 shadow-[0_0_0_1px_rgba(6,182,212,0.25)]'
                  : 'bg-gray-800 border-gray-700 hover:border-cyan-500/60',
              dragOverItemId === item.id && dragOverStatus === col.status
                ? dragOverAfter
                  ? 'border-b-2 border-b-cyan-400'
                  : 'border-t-2 border-t-cyan-400'
                : '',
            ]"
            :title="isSelected(item.id)
              ? 'Selected — Shift+click to extend, Ctrl+click to toggle, click to deselect & copy'
              : 'Click to copy · Shift+click to range-select · Ctrl+click to toggle'"
          >
            <!-- Top row: type badge + name + selection tick -->
            <div class="flex items-start gap-2">
              <span
                :class="[
                  'text-xs font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded shrink-0',
                  item.item_type === 'mix'
                    ? 'bg-purple-900/60 text-purple-300'
                    : 'bg-blue-900/60 text-blue-300',
                ]"
              >{{ item.item_type }}</span>
              <span class="text-sm font-medium text-white leading-snug break-words flex-1">{{ item.name }}</span>
              <!-- Selection checkmark -->
              <span
                v-if="isSelected(item.id)"
                class="shrink-0 mt-0.5 text-cyan-400"
                title="Selected"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>

            <!-- Actions row -->
            <div class="flex items-center justify-between mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-xs text-gray-500 font-mono truncate max-w-32">{{ item.tidal_id }}</span>
              <div class="flex gap-1">
                <!-- Info button -->
                <button
                  @click.stop="infoItem = item"
                  class="text-gray-400 hover:text-cyan-400 transition p-1 rounded"
                  title="Show info"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
                <!-- Remove button -->
                <button
                  @click.stop="deleteItem(item)"
                  class="text-gray-500 hover:text-red-400 transition p-1 rounded"
                  title="Remove from list"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Modal -->
    <Teleport to="body">
      <div
        v-if="infoItem"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
        @click.self="infoItem = null"
      >
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
          <!-- Modal header -->
          <div class="flex items-start justify-between mb-5">
            <div>
              <span
                :class="[
                  'text-xs font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded mr-2',
                  infoItem.item_type === 'mix'
                    ? 'bg-purple-900/60 text-purple-300'
                    : 'bg-blue-900/60 text-blue-300',
                ]"
              >{{ infoItem.item_type }}</span>
              <h3 class="text-xl font-bold text-white mt-2">{{ infoItem.name }}</h3>
            </div>
            <button @click="infoItem = null" class="text-gray-500 hover:text-white transition ml-4 mt-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Info rows -->
          <div class="space-y-3">
            <!-- ID -->
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">ID</p>
              <div class="flex items-center gap-2">
                <code class="flex-1 bg-gray-900 text-cyan-300 text-sm rounded px-3 py-2 font-mono break-all">{{ infoItem.tidal_id }}</code>
                <button
                  @click="copyToClipboard(infoItem!.tidal_id, 'ID copied!')"
                  class="flex-shrink-0 text-gray-400 hover:text-cyan-400 transition p-2 rounded hover:bg-gray-700"
                  title="Copy ID"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Short URL -->
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Short URL</p>
              <div class="flex items-center gap-2">
                <code class="flex-1 bg-gray-900 text-green-300 text-sm rounded px-3 py-2 font-mono break-all">{{ shortPath(infoItem) }}</code>
                <button
                  @click="copyToClipboard(shortPath(infoItem!), 'Short URL copied!')"
                  class="flex-shrink-0 text-gray-400 hover:text-green-400 transition p-2 rounded hover:bg-gray-700"
                  title="Copy short URL"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Long URL -->
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Long URL</p>
              <div class="flex items-center gap-2">
                <code class="flex-1 bg-gray-900 text-yellow-300 text-sm rounded px-3 py-2 font-mono break-all">{{ longUrl(infoItem) }}</code>
                <button
                  @click="copyToClipboard(longUrl(infoItem!), 'Long URL copied!')"
                  class="flex-shrink-0 text-gray-400 hover:text-yellow-400 transition p-2 rounded hover:bg-gray-700"
                  title="Copy long URL"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <button
            @click="infoItem = null"
            class="mt-6 w-full bg-gray-700 hover:bg-gray-600 text-white rounded-lg py-2 transition"
          >
            Close
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
