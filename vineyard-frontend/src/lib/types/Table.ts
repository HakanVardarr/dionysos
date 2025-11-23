export type Column = { key: string; label: string };
export type Action = {
    label: string;
    colorClass?: string;
    callback: (item: any) => void;
};
