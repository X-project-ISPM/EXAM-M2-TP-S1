export interface EditorContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  selectedText: string;
}

export interface SidebarPanel {
  id: string;
  title: string;
  isOpen: boolean;
}
