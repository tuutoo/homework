<script setup lang="ts">
import { ref } from "vue";
import { NCard, NButton, NSpace } from "naive-ui";
import axios from "axios";

import 'vue-cropper/dist/index.css'
import { VueCropper }  from "vue-cropper";

const apiUrl = import.meta.env.VITE_APP_API_URL || "http://192.168.66.32:8000/invert/";

const imgSrc = ref("");
const imgReturn = ref("");
const infoText = ref("");
const fileInput = ref<HTMLInputElement | null>(null);
const cropper = ref<{ getCropBlob: (callback: (data: Blob) => void) => void } | null>(
  null
);

const clearPreviousResults = () => {
  imgSrc.value = "";
  imgReturn.value = "";
  infoText.value = "";
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const clickInputFile = () => {
  fileInput?.value?.click();
};

const fetchRequest = async (formData: FormData) => {
  infoText.value = "正在处理文件中...";
  try {
    const { data } = await axios.post(apiUrl, formData, {
      responseType: "arraybuffer",
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    const blob = new Blob([data], { type: "image/jpeg" });
    imgReturn.value = URL.createObjectURL(blob);
    infoText.value = "文件处理成功";
  } catch (error) {
    infoText.value = "文件处理失败";
  }
};

const fileChanged = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files ? target.files[0] : null;
  if (!file) {
    return;
  }
  clearPreviousResults();
  imgSrc.value = URL.createObjectURL(file);
  const formData = new FormData();
  formData.append("file", file);
  fetchRequest(formData);
};

const downloadImage = () => {
  console.log("downloading");
  const aLink = document.createElement("a");
  aLink.download = "反色图像";
  cropper.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data);
    aLink.click();
  });
};
</script>

<template>
  <div class="container">
    <n-card title="请上传需要反色处理的图片">
      <n-space vertical>
        <n-space>
          <n-button @click="clickInputFile">上传文件</n-button>
        </n-space>
        <div>
          <input type="file" ref="fileInput" @change="fileChanged" hidden />
          <img :src="imgSrc" alt="" class="scaled-img" />
          <div class="content">
            <p>{{ infoText }}</p>
          </div>
        </div>
      </n-space>
      <div class="finalResult">
        <n-space vertical>
          <div class="crop-container">
            <VueCropper
              ref="cropper"
              :img="imgReturn"
              autoCrop
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
          <n-button @click="downloadImage">下载裁切图</n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 50%;
}

.scaled-img {
  max-width: 100%;
  height: auto;
}

.crop-container {
  width: 100%;
  height: 600px;
}
</style>
